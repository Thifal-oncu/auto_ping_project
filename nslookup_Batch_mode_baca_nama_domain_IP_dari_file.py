# --- Tambahan: batch concurrent & auto-PTR ---
from concurrent.futures import ThreadPoolExecutor, as_completed

def auto_qtype_for_target(target: str, requested_qtype: str):
    """Jika user memberikan 'auto' buat PTR otomatis ketika target IP; atau kembalikan requested_qtype."""
    if requested_qtype.upper() == "AUTO":
        return "PTR" if is_ip(target) else "A"
    return requested_qtype

def process_batch_concurrent(targets: list, args, max_workers: int = 10, out_file: str = None):
    """
    Jalankan batch concurrent untuk list targets.
    - args: parsed args
    - max_workers: jumlah thread
    - out_file: jika tidak None, tulis hasil JSON gabungan ke file
    """
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        future_map = {}
        for t in targets:
            qtype = auto_qtype_for_target(t, args.type)
            # gunakan process_target untuk 1 target tapi pastikan tidak memanggil monitor mode dan compare mode
            future = ex.submit(process_target_single, t, qtype, args)
            future_map[future] = (t, qtype)
        for fut in as_completed(future_map):
            t, qtype = future_map[fut]
            try:
                r = fut.result()
                results.extend(r if isinstance(r, list) else [r])
            except Exception as e:
                logger.error(f"Error processing {t}: {e}")
                results.append({"target": t, "qtype": qtype, "server": None, "answers": [], "error": str(e)})
    # optional write to file
    if out_file:
        import json
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    return results

# Helper kecil: panggil process_target untuk single target tapi return struktur yang konsisten (dipakai oleh thread)
def process_target_single(target: str, qtype: str, args):
    # Sederhanakan: buat args-like object dengan server/timeout/lifetime/json/retries
    class A: pass
    a = A()
    a.server = args.server
    a.timeout = args.timeout
    a.lifetime = args.lifetime
    a.json = args.json
    a.compare = False
    a.retries = args.retries
    # panggil process_target yang sudah ada — ini akan mengembalikan list/struktur konsisten
    return process_target(target, a)
