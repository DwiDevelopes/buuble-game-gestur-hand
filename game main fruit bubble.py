import cv2
import time
import random
import mediapipe as mp
import numpy as np
import pygame  

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Game variables
Fruits = []
Obstacles = []
Score = 0
Lives = 200  # Pemberian nyawa dan waktu
Fruit_Size = 30
Obstacle_Size = 30
Game_Over = False


pygame.init()
pygame.mixer.music.load("background_music.mp3")  
pygame.mixer.music.play(-1, 0.0)  

# Load sound effects
point_sound = pygame.mixer.Sound("point_sound.wav")  # Sound after getting points
game_over_sound = pygame.mixer.Sound("game_over_sound.wav")  # Sound when game over


# Function to reset game
def Reset_Game():
    global Fruits, Obstacles, Score, Lives, Game_Over
    Fruits = []
    Obstacles = []
    Score = 0
    Lives = 200
    Game_Over = False


# Function to spawn fruits
def Spawn_Fruits():
    fruit = {}
    random_x = random.randint(15, 600 - Fruit_Size)
    random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    fruit["Color"] = random_color
    fruit["Curr_position"] = [random_x, 440]  # Start at the bottom of the screen
    Fruits.append(fruit)


# Function to spawn obstacles
def Spawn_Obstacle():
    obstacle = {}
    random_x = random.randint(15, 600 - Obstacle_Size)
    obstacle["Color"] = (0, 0, 255)  # Red color for obstacles
    obstacle["Curr_position"] = [random_x, 440]  # Start at the bottom of the screen
    Obstacles.append(obstacle)


# Function to handle fruit movement
def Fruit_Movement():
    global Lives
    for fruit in Fruits:
        fruit["Curr_position"][1] -= 5  # Move fruit upwards
        if fruit["Curr_position"][1] < 20:  # If fruit goes off the screen
            Lives -= 1
            Fruits.remove(fruit)


# Function to handle obstacle movement
def Obstacle_Movement():
    global Lives
    for obstacle in Obstacles:
        obstacle["Curr_position"][1] -= 5  # Move obstacle upwards
        if obstacle["Curr_position"][1] < 20:  # If obstacle goes off the screen
            Obstacles.remove(obstacle)
        if obstacle["Curr_position"][1] < 440 and obstacle["Curr_position"][1] > 430:
            # Check if obstacle hits the bottom where player is
            Lives -= 1
            Obstacles.remove(obstacle)


# Function to draw fruits on the screen
def Draw_Fruits(img):
    for fruit in Fruits:
        cv2.circle(img, (fruit["Curr_position"][0], fruit["Curr_position"][1]), Fruit_Size, fruit["Color"], -1)


# Function to draw obstacles on the screen
def Draw_Obstacles(img):
    for obstacle in Obstacles:
        cv2.rectangle(img, (obstacle["Curr_position"][0] - Obstacle_Size // 2, obstacle["Curr_position"][1] - Obstacle_Size // 2),
                      (obstacle["Curr_position"][0] + Obstacle_Size // 2, obstacle["Curr_position"][1] + Obstacle_Size // 2),
                      obstacle["Color"], -1)


# Function to check if a fruit is sliced
def Check_Slice(hands_landmarks):
    global Score
    for hand_landmarks in hands_landmarks:  # Iterate through all hands
        if hand_landmarks:
            # Resolusi gambar 640x480 yang tampil di layar
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_x = int(index_finger_tip.x * 640)
            index_y = int(index_finger_tip.y * 480)

            # Check for collision with fruits
            for fruit in Fruits:
                fruit_x, fruit_y = fruit["Curr_position"]
                if fruit_x - Fruit_Size < index_x < fruit_x + Fruit_Size and fruit_y - Fruit_Size < index_y < fruit_y + Fruit_Size:
                    Fruits.remove(fruit)
                    Score += 1  # When you slice the fruit, you get 1 point
                    point_sound.play()  # Play point sound


# Function to display the score on the screen
def Display_Score(img):
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, f'Final Score: {Score}', (200, 200), font, 1, (0, 255, 0), 2)


# Main function to run the game
def main():
    global Lives, Game_Over
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        success, img = cap.read()
        if not success:
            continue

        img = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)
        results = hands.process(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            Check_Slice(results.multi_hand_landmarks)  # Check slices for multiple hands
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        if Lives <= 0:
            Display_Score(img)
            game_over_sound.play()  # Play the game over sound
            time.sleep(2)  # Display score and wait for 2 seconds
            Game_Over = True  # Game over state
            Reset_Game()

        # Game logic
        if not Game_Over:
            if len(Fruits) < 5:  # Spawn fruits when less than 5
                Spawn_Fruits()

            if len(Obstacles) < 3:  # Spawn obstacles when less than 3
                Spawn_Obstacle()

            Fruit_Movement()
            Obstacle_Movement()
            Draw_Fruits(img)
            Draw_Obstacles(img)

            # Display score and time
            cv2.putText(img, f'Score : {Score}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(img, f'Time : {Lives}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Key press handling for restart or quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Press 'q' to quit
            break
        elif key == ord('r') and Game_Over:  # Press 'r' to restart
            Reset_Game()

        cv2.imshow("Fruit Ninja", img)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
