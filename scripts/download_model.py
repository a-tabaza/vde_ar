from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="silma-ai/silma-embeddding-sts-v0.1",
    local_dir="../models/silma-embeddding-sts-v0.1",
)
