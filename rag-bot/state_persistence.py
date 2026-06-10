def _load_pending_from_postgres(
    status: Optional[str] = "pending",
    limit: int = 50,
    beta_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    sql = """
        SELECT beta_id, action_id, idemp_key, signal_type, action_type,
               suggested_message, status, created_at, executed_at,
               dry_run, block_reason, metadata
        FROM hv_pending_actions
        WHERE 1=1
    """
    params: list = []
    if beta_id:
        sql += " AND beta_id = %s"
        params.append(beta_id)
    if status:
        sql += " AND status = %s"
        params.append(status)
    sql += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)

    actions: List[Dict[str, Any]] = []
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            for row in cur.fetchall():
                actions.append({
                    "beta_id": row[0],
                    "action_id": row[1],
                    "idemp_key": row[2],
                    "signal": {"signal_type": row[3]},
                    "action_type": row[4],
                    "suggested_message": row[5],
                    "status": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                    "executed_at": row[8].isoformat() if row[8] else None,
                    "dry_run": row[9],
                    "block_reason": row[10],
                    "metadata": row[11] or {},
                })
    return actions

def _persist_pending_to_postgres(action: Dict[str, Any]) -> None:
    sql = """
        INSERT INTO hv_pending_actions
            (beta_id, action_id, idemp_key, signal_type, action_type,
             suggested_message, status, created_at, dry_run, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (idemp_key) DO NOTHING
    """
    params = (
        action.get("beta_id"),
        action.get("action_id"),
        action.get("idemp_key"),
        (action.get("signal") or {}).get("signal_type"),
        action.get("action_type"),
        action.get("suggested_message"),
        action.get("status", "pending"),
        action.get("created_at"),
        action.get("dry_run", False),
        action.get("metadata") or {},
    )
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)

def _mark_executed_in_postgres(
    action_id: str,
    idemp_key: str,
    *,
    dry_run: bool = False,
    executed_at: Optional[str] = None,
    block_reason: Optional[Dict] = None,
    final_status: Optional[str] = None,
) -> None:
    status = final_status or ("dry_run_executed" if dry_run else "executed")
    sql = """
        UPDATE hv_pending_actions
        SET status = %s,
            executed_at = COALESCE(%s, NOW()),
            dry_run = %s,
            block_reason = %s
        WHERE action_id = %s OR idemp_key = %s
    """
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (
                status,
                executed_at,
                dry_run,
                json.dumps(block_reason) if block_reason else None,
                action_id,
                idemp_key,
            ))

def _is_idemp_executed_pg(idemp_key: str) -> bool:
    if not idemp_key:
        return False
    sql = """
        SELECT 1 FROM hv_pending_actions
        WHERE idemp_key = %s
          AND status IN ('executed', 'dry_run_executed', 'already_executed')
        LIMIT 1
    """
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (idemp_key,))
            return cur.fetchone() is not None

def load_pending_actions(
    status: Optional[str] = "pending",
    limit: int = 50,
    beta_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    mode = _persistence_mode()
    prefer_postgres = mode in ("postgres", "dual") and _is_postgres_available()
    if prefer_postgres:
        try:
            actions = _load_pending_from_postgres(status=status, limit=limit, beta_id=beta_id)
            if actions:
                return actions
            return _load_pending_from_files(status=status, limit=limit, beta_id=beta_id)
        except Exception as e:
            print(f"[state-persistence] WARN: postgres load_pending failed: {e}. Falling back to files.")
            return _load_pending_from_files(status=status, limit=limit, beta_id=beta_id)
    return _load_pending_from_files(status=status, limit=limit, beta_id=beta_id)

def persist_pending_action(action: Dict[str, Any]) -> None:
    mode = _persistence_mode()
    do_postgres = mode in ("postgres", "dual") and _is_postgres_available()
    if do_postgres:
        try:
            _persist_pending_to_postgres(action)
            if mode == "dual":
                _persist_pending_to_file(action)
            return
        except Exception as e:
            print(f"[state-persistence] WARN: postgres persist_pending failed: {e}. Falling back to files.")
    _persist_pending_to_file(action)

def mark_pending_executed(
    action: Dict[str, Any],
    *,
    dry_run: bool = False,
    executed_at: Optional[str] = None,
    block_reason: Optional[Dict] = None,
    final_status: Optional[str] = None,
) -> None:
    mode = _persistence_mode()
    do_postgres = mode in ("postgres", "dual") and _is_postgres_available()
    if do_postgres:
        try:
            _mark_executed_in_postgres(
                action.get("action_id", ""),
                action.get("idemp_key", ""),
                dry_run=dry_run,
                executed_at=executed_at,
                block_reason=block_reason,
                final_status=final_status,
            )
            if mode == "dual":
                _mark_executed_in_file(action, dry_run=dry_run, final_status=final_status)
            return
        except Exception as e:
            print(f"[state-persistence] WARN: postgres mark_executed failed: {e}. Using files.")
    _mark_executed_in_file(action, dry_run=dry_run, final_status=final_status)

def is_idemp_already_executed(idemp_key: str) -> bool:
    mode = _persistence_mode()
    prefer_postgres = mode in ("postgres", "dual") and _is_postgres_available()
    if prefer_postgres:
        try:
            if _is_idemp_executed_pg(idemp_key):
                return True
        except Exception as e:
            print(f"[state-persistence] WARN: postgres idemp check failed: {e}. Falling to files.")
    return _is_idemp_executed_file(idemp_key)

def _pending_dir() -> Path:
    raw = os.getenv("HV_PENDING_ACTIONS_DIR", "data/pending_actions")
    p = Path(raw)
    p.mkdir(parents=True, exist_ok=True)
    return p

def _pending_file() -> Path:
    return _pending_dir() / "pending_actions.jsonl"

def _executed_file() -> Path:
    return _pending_dir() / "executed_actions.jsonl"

def _load_pending_from_files(
    status: Optional[str] = "pending",
    limit: int = 50,
    beta_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    path = _pending_file()
    if not path.exists():
        return []
    actions: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                a = json.loads(line)
                if status is None or a.get("status") == status:
                    if beta_id is None or a.get("beta_id") == beta_id:
                        actions.append(a)
            except Exception:
                continue
    return actions[-limit:][::-1] if limit else actions

def _persist_pending_to_file(action: Dict[str, Any]) -> None:
    path = _pending_file()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(action, ensure_ascii=False) + "\n")

def _mark_executed_in_file(
    action: Dict[str, Any],
    *,
    dry_run: bool = False,
    final_status: Optional[str] = None,
) -> None:
    exec_path = _executed_file()
    action = dict(action)
    action["status"] = final_status or ("dry_run_executed" if dry_run else "executed")
    action["executed_at"] = _utc_now()
    with exec_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(action, ensure_ascii=False) + "\n")
    pending_path = _pending_file()
    if pending_path.exists():
        remaining = []
        with pending_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                    if a.get("action_id") != action.get("action_id"):
                        remaining.append(a)
                except Exception:
                    remaining.append(line)
        tmp = pending_path.with_name(pending_path.name + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            for a in remaining:
                if isinstance(a, dict):
                    f.write(json.dumps(a, ensure_ascii=False) + "\n")
                else:
                    f.write(str(a) + "\n")
        os.replace(tmp, pending_path)

def _is_idemp_executed_file(idemp_key: str) -> bool:
    if not idemp_key:
        return False
    exec_path = _executed_file()
    if not exec_path.exists():
        return False
    try:
        with exec_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                    if e.get("idemp_key") == idemp_key:
                        return True
                except Exception:
                    continue
    except Exception:
        pass
    return False
