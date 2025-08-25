import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.auth.auth_endpoints import router as auth_router
from app.api.endpoints.users.user_endpoints import router as users_router
from app.api.endpoints.video.upload_video import router as upload_video_router
from app.api.endpoints.video.import_video import router as import_video_router
from app.core.security.headers_middleware import SecurityHeadersMiddleware
from app.core.security.csrf_middleware import CSRFMiddleware


def _maybe_enable_debugpy():
    """
    Conditionally enable debugpy remote debugging.

    Enable by setting:
      DEBUGPY=1
      (optional) DEBUG_LISTEN=0.0.0.0:5678
      (optional) DEBUG_WAIT_FOR_CLIENT=1  -> block until IDE attaches

    Safe to leave in production image (no effect unless DEBUGPY=1).
    """
    if os.environ.get("DEBUGPY", "0") == "1":
        host_port = os.environ.get("DEBUG_LISTEN", "0.0.0.0:5678")
        try:
            import debugpy  # type: ignore
            host, port = host_port.split(":")
            if not debugpy.is_client_connected():
                debugpy.listen((host, int(port)))
                if os.environ.get("DEBUG_WAIT_FOR_CLIENT", "0") == "1":
                    print(f"[debugpy] Waiting for client at {host_port} ...", flush=True)
                    debugpy.wait_for_client()
                print(f"[debugpy] Debugger listening at {host_port}", flush=True)
        except Exception as e:
            # Swallow errors so the app still starts
            print(f"[debugpy] Failed to initialize debugger: {e}", flush=True)


_maybe_enable_debugpy()

app = FastAPI()

app.add_middleware(CSRFMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(users_router, tags=["Users"])
app.include_router(upload_video_router, tags=["Video"])
app.include_router(import_video_router, tags=["Video"])
