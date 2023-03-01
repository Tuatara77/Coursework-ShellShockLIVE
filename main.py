import json
try: import pygame
except ModuleNotFoundError:
    import os
    os.system("pip install pygame")
    try: import pygame
    except: 
        os.system("python main.py")
        exit()
try: import numpy
except ModuleNotFoundError:
    import os
    os.system("pip install numpy")
    try: import numpy
    except: 
        os.system("python main.py")
        exit()
with open("constants.json", "r") as constants: const = json.load(constants)


def main(): # main function
    pygame.init() # initialise pygame
    
    FULLSCREEN = True

    const["screenwidth"] = pygame.display.Info().current_w # add the screen width to consants dictionary
    const["screenheight"] = pygame.display.Info().current_h # add the screen height to consants dictionary
    with open("constants.json", "w") as constants: json.dump(const, constants, sort_keys=False, indent=4)
    scalar = 2

    # const["screenwidth"] = 1536 # add the screen width to consants dictionary
    # const["screenheight"] = 864 # add the screen height to consants dictionary
    # with open("constants.json", "w") as constants: json.dump(const, constants, sort_keys=False, indent=4)
    # scalar = 1

    if FULLSCREEN:
        screen = pygame.display.set_mode([const["screenwidth"], 
                                          const["screenheight"]], pygame.FULLSCREEN) # initialise fullscreen
    else:
        const["screenwidth"] //= scalar
        const["screenheight"] //= scalar
        screen = pygame.display.set_mode([const["screenwidth"], 
                                          const["screenheight"]]) # initialise windowed screen

    from menu import mainMenu

    mainMenu(screen)
    pygame.quit() # kill pygame


if __name__ == "__main__":
    main()