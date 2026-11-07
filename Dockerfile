FROM python:3.12-slim

# CJK fonts first: without them the renderer raises instead of drawing boxes
RUN apt-get update \
 && apt-get install -y --no-install-recommends fonts-noto-cjk \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir xhs-cards

WORKDIR /work
ENTRYPOINT ["xhs-cards"]
CMD ["--help"]
