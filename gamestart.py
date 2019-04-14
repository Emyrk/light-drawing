import cv2
from halo import Halo
from colorama import init as colorama_init, Fore
from GameEngine import GameEngine
from Utility import HideOutput

colorama_init()


def enum_cameras():
    spinner = Halo(text="Detecting cameras (please click 'Allow' on any permission dialogs)",
                   text_color="yellow", spinner="dots")
    spinner.start()

    with HideOutput():
        idx = 0
        cameras = {}
        while True:
            cap = cv2.VideoCapture(idx)
            if not cap.read()[0]:
                break
            else:
                cameras[idx] = {
                    "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    "fps": int(cap.get(cv2.CAP_PROP_FPS))
                }
            cap.release()
            idx += 1

    spinner.succeed()

    return cameras


def choose_camera():
    cameras = enum_cameras()
    camera_id = 0

    if len(cameras) > 1:
        for idx, props in cameras.items():
            print(f"[{idx}] {props['width']}x{props['height']} @ {props['fps']}fps")

        while True:
            try:
                camera_id = int(input(Fore.YELLOW + f"Choose a camera [0-{len(cameras) - 1}]: " + Fore.RESET))
            except ValueError:
                print(Fore.RED + "Invalid selection, try again." + Fore.RESET)
                continue

            if 0 <= camera_id < len(cameras):
                break

            print(Fore.RED + "Invalid selection, try again." + Fore.RESET)

    return camera_id


def main():
    game = GameEngine(choose_camera())
    game.run_engine()


if __name__ == "__main__":
    main()
