import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="DocOS Studio — local film production app")
    parser.add_argument("--port", type=int, default=8876)
    args = parser.parse_args()
    uvicorn.run("studio_api.app:create_app", factory=True, host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
