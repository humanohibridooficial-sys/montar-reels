# Cualquiera lo instala en su equipo y le funciona (11-10-2026)

Qué es: que una persona cualquiera (con Windows y Claude Code) siga una guía, lance el instalador y
termine con el editor funcionando con SU marca y SU estilo, sin nada de Luismi dentro.

## Lo que fallaba (visto al montar la T42 en el PC de Luismi, 10-10)
1. El catálogo (`mi-estilo/recursos.md`) está fuera de git: una persona nueva no tiene ninguno.
2. Los agentes director y revisor llevan la marca y el nombre de FF360 escritos dentro.
3. Los agentes solo existen si se abre Claude Code dentro del repo; el instalador no los copia.
4. Nada comprueba CapCut: ni la plantilla ni la versión (con 10.x rechaza los proyectos).
5. Nada comprueba que esté Claude Code.
6. No hay una guía paso a paso para quien no programa.

## Cambios
- `mi-estilo/recursos.ejemplo.md`: el catálogo genérico (funciones, formas, tonos, regla de grabación),
  sin cuentas ni marca de nadie. El instalador lo copia a `recursos.md` si no existe.
- Agentes genéricos: leen la marca de `config.json` (`color_clave`, `color_marca`) y de `mi-estilo/estilo.md`;
  el instalador los copia a `~/.claude/agents/` con la ruta del repo.
- `comprobar.ps1`: revisa todo de nuevo cuando se quiera y termina con un control positivo (escribe un
  borrador de CapCut en memoria con pyJianYingDraft). Dice qué falta y cómo arreglarlo.
- `instalar.ps1`: copia el catálogo de ejemplo y los agentes, avisa si falta Claude Code y llama a
  `comprobar.ps1` al final.
- `docs/PASO-A-PASO.md`: la guía para quien no programa.

## Hecho cuando
`comprobar.ps1` pasa en el PC de Luismi (control) y una carpeta nueva, siguiendo solo la guía, llega a
"todo listo" sin tocar nada a mano salvo la plantilla de CapCut.

## Bitácora
- 11-10: spec.
- 11-10: hecho. Control en el PC de Luismi (su Python): marca 4 faltas reales (faster_whisper en ese Python,
  skill y 2 agentes sin instalar) y el control positivo pasa. Copia limpia clonada de GitHub: marca las 10
  faltas de un equipo nuevo, cada una con su paso del instalador. NO probado: lanzar instalar.ps1 de principio
  a fin en un equipo limpio (en el de Luismi sobrescribiría su skill y sus agentes con la ruta de prueba).
