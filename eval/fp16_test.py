import json, resource, time
from pathlib import Path
import numpy as np, onnx
from onnxconverter_common import float16
src = Path("results/clap_audio.onnx"); dst = Path("results/clap_audio_fp16.onnx")
if not dst.exists():
    m = onnx.load(str(src)); m16 = float16.convert_float_to_float16(m, keep_io_types=True); onnx.save(m16, str(dst))
print("fp16 size:", dst.stat().st_size // 1_000_000, "MB")
import onnxruntime as ort, librosa
so = ort.SessionOptions(); so.intra_op_num_threads = 1; so.enable_mem_pattern = False; so.enable_cpu_mem_arena = False
sess = ort.InferenceSession(str(dst), so, providers=["CPUExecutionProvider"])
z = np.load("../data/clap.npz"); ref = dict(zip(z["ids"].tolist(), z["emb"]))
S = json.load(open("sample.json"))[:15]; sims = []; t0 = time.time()
for s in S:
    y = librosa.resample(np.load(f"cache/{s['deezer_id']}.npy").astype("float32"), orig_sr=22050, target_sr=48000)[:480000]
    y = np.pad(y, (0, max(0, 480000 - len(y))))
    e = sess.run(None, {"wav": y[None, :]})[0][0]; r = ref[s["deezer_id"]]
    sims.append(float(np.dot(e / np.linalg.norm(e), r / np.linalg.norm(r))))
print(f"agreement with full CLAP: mean {np.mean(sims):.3f}, worst {np.min(sims):.3f}")
print(f"time per track: {(time.time() - t0) / len(S):.2f}s, peak memory {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.0f} MB")
