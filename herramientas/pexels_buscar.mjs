// Busca vídeos verticales en Pexels (b-roll con licencia para anuncios). Uso: node herramientas/pexels_buscar.mjs "query 1" "query 2" ...
// La clave PEXELS_API_KEY se lee del .env de la carpeta del repo y no se imprime. Gratis en https://www.pexels.com/api/
import path from 'node:path'
import { fileURLToPath } from 'node:url'
try { process.loadEnvFile(path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '.env')) } catch {}
const KEY = process.env.PEXELS_API_KEY
if (!KEY) { console.error('Falta PEXELS_API_KEY en el archivo .env de la carpeta editor-reels'); process.exit(1) }
for (const q of process.argv.slice(2)) {
  const r = await fetch(`https://api.pexels.com/videos/search?query=${encodeURIComponent(q)}&orientation=portrait&per_page=12`, { headers: { Authorization: KEY } })
  const j = await r.json()
  console.log(`\n## ${q}  (${j.total_results})`)
  for (const v of j.videos ?? []) {
    const f = (v.video_files ?? []).filter(x => x.height >= 1900 && x.height <= 2100 && x.width <= 1100).sort((a, b) => a.height - b.height)[0]
    if (!f) continue
    console.log(`${v.id}\t${v.duration}s\t${f.width}x${f.height}\t${v.user?.name}\t${v.url.replace('https://www.pexels.com/video/', '')}\t${f.link}`)
  }
}
