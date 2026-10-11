"""Cut CLAP down to just its listening part (audio branch) and save it as a compact ONNX file
that can run on the small free server. Then check it gives the same fingerprints as full CLAP."""
from pathlib import Path
import numpy as np, torch, laion_clap

ROOT = Path(__file__).resolve().parent.parent
m = laion_clap.CLAP_Module(enable_fusion=False, amodel="HTSAT-base")
m.load_ckpt(str(Path.home() / ".cache/laion_clap/music_audioset_epoch_15_esc_90.14.pt"))
model = m.model.eval()

class AudioOnly(torch.nn.Module):
    def __init__(s, mdl):
        super().__init__(); s.m = mdl
    def forward(s, wav):                      # wav: (1, 480000) at 48 kHz
        out = s.m.encode_audio({"waveform": wav, "longer": torch.tensor([False])}, device="cpu")
        emb = s.m.audio_projection(out["embedding"])
        return torch.nn.functional.normalize(emb, dim=-1)

a = AudioOnly(model).eval()
x = torch.randn(1, 480000) * 0.1
with torch.no_grad():
    ref = m.get_audio_embedding_from_data(x=x.numpy(), use_tensor=False)
    mine = a(x).numpy()
print("matches full CLAP:", float(np.dot(ref[0] / np.linalg.norm(ref[0]), mine[0])))
n_params = sum(p.numel() for p in a.parameters() if True)
print("audio params (all, incl. unused text):", n_params)
out = ROOT / "eval" / "results" / "clap_audio.onnx"
torch.onnx.export(a, x, str(out), input_names=["wav"], output_names=["emb"], opset_version=17, dynamo=False)
print("saved", out, out.stat().st_size // 1_000_000, "MB")
