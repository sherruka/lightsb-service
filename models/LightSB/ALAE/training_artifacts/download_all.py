import dlutils
from packaging import version

if not hasattr(dlutils, "__version__") or version.parse(
    dlutils.__version__
) < version.parse("0.0.11"):
    raise RuntimeError("Please update dlutils: pip install dlutils --upgrade")

try:
    dlutils.download.from_google_drive(
        "18BzFYKS3icFd1DQKKTeje7CKbEKXPVug", directory="training_artifacts/ffhq"
    )
except IOError:
    dlutils.download.from_url(
        "https://alaeweights.s3.us-east-2.amazonaws.com/ffhq/model_157.pth",
        directory="training_artifacts/ffhq",
    )
