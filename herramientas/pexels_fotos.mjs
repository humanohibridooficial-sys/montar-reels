// Busca FOTOS en Pexels (para recortar objetos). Uso: node herramientas/pexels_fotos.mjs "query" ...
// La clave PEXELS_API_KEY se lee del .env de la carpeta del repo y no se imprime.
import path from 'node:path'
import { fileURLToPath } from 'node:url'
try { process.loadEnvFile(path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '.env')) } catch {}
const KEY = process.env.PEXELS_API_KEY
if (!KEY) { console.error('Falta PEXELS_API_KEY en el archivo .env de la carpeta editor-reels'); process.exit(1) }
for (const q of process.argv.slice(2)) {
  const r = await fetch(`https://api.pexels.com/v1/search?query=${encodeURIComponent(q)}&per_page=10`, { headers: { Authorization: KEY } })
  const j = await r.json()
  console.log(`\n## ${q} (${j.total_results})`)
  for (const p of j.photos ?? []) console.log(`${p.id}\t${p.width}x${p.height}\t${p.alt?.slice(0,70)}\t${p.src.large2x}`)
}
