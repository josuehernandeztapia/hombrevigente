# Gate A — Primera invitación beta (HV)

**Canal:** tu **WhatsApp personal** · Sin número HV · Sin Twilio  
**Tally:** https://tally.so/r/5BVeRd

---

## Antes de enviar (checklist)

- [ ] P1 Caso #0: mensaje #4 guardado en Notas
- [ ] Tracker en Sheets o xlsx actualizado
- [ ] Sabes cómo responder si hay bandera screening (script #3)
- [ ] **Opcional recomendado:** médico aliado con SLA — si no hay, usar texto honesto abajo

---

## Mensaje #1 — Invitación (copiar desde tu cel)

```
Qué onda [nombre] 👋 Estoy probando algo y quiero invitarte como de los primeros.

Se llama Hombre Vigente: te armo un protocolo personalizado de optimización (energía, recuperación, piel, longevidad) con tus datos — foto, labs si tienes, wearable si usas.

Son 5–10 personas gratis, 4 semanas, a cambio de feedback honesto. Todo es información educativa — no vendo medicamentos; tú validas con tu médico.

¿Te late entrar?
```

---

## Si dice que sí

**Con médico en cola / SLA:**
```
Va 🙌 Llena esto (5 min): https://tally.so/r/5BVeRd
En 24–48h te mando tu protocolo, después de revisión médica.
```

**Sin médico aliado aún (honesto MVP-0):**
```
Va 🙌 Llena esto (5 min): https://tally.so/r/5BVeRd
Te armo el protocolo en 24–48h. Es educativo y conservador; si hay algo de salud delicado, lo vemos contigo y con tu médico antes de que inicies nada.
```

---

## Después del sí

1. Fila nueva en **Pipeline** (`tracker_pipeline_row.py` tras Tally)
2. Estado Sheets: `lead` → `onboarding enviado`
3. Recordatorio día 2 si no llena Tally (script #2)

---

## A quién NO invitar todavía

- Desconocidos fríos (sin confianza)
- Quien espere bot / app / número oficial HV
- Masivo en listas — solo 1:1 personal

---

*P4 cuando 1 persona complete Tally + screening*