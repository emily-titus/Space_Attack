
import arcade
import random

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Space Invaders"
PLAYER_SPEED = 300
BULLET_SPEED = 500
ENEMY_ROWS = 3
ENEMY_COLUMNS = 8
ENEMY_SPEED = 80
ENEMY_BULLET_SPEED = 250
MAX_LEVEL = 3


class Game(arcade.Window):

    def __init__(self):
        super().__init__(
            WINDOW_WIDTH, 
            WINDOW_HEIGHT, 
            WINDOW_TITLE
        )

        self.background_color = arcade.color.BABY_BLUE


    def setup(self):
        """Reset the game to the initial state."""
        self.player_x = WINDOW_WIDTH // 2
        self.left_pressed = False
        self.right_pressed = False
        self.bullets = []
        self.enemies = []
        self.level = 1
        self.score = 0
        self.enemy_direction = 1
        self.game_won = False
        self.game_over = False
        self.enemy_bullets = []
        self.enemy_shot_timer = 1.0
        self.lives = 3
        self.clouds = []
        self.create_enemies()

        for _ in range(8):
            cloud_x = random.randint(70, WINDOW_WIDTH - 70)
            cloud_y = random.randint(150, WINDOW_HEIGHT - 60)
            cloud_scale = random.choice([1, 1, 2])

            self.clouds.append([cloud_x, cloud_y, cloud_scale])

        self.player_sprite = arcade.Sprite(
            ":resources:images/space_shooter/playerShip3_orange.png",
            scale=0.5
        )
        self.player_sprite.center_x = self.player_x
        self.player_sprite.center_y = 55


    def on_draw(self):
        self.clear()

        for cloud in self.clouds:
            cloud_x, cloud_y, scale = cloud
            cloud_color = (180, 180, 200)

            arcade.draw_lbwh_rectangle_filled(
                cloud_x - 35 * scale,
                cloud_y - 12 * scale,
                70 * scale, 
                20 * scale,
                cloud_color
            )

            arcade.draw_circle_filled(
                cloud_x - 25 * scale,
                cloud_y + 5 * scale,
                18 * scale,
                cloud_color
            )

            arcade.draw_circle_filled(
                cloud_x, 
                cloud_y + 12 * scale,
                25 * scale,
                cloud_color
            )

            arcade.draw_circle_filled(
                cloud_x + 25 * scale,
                cloud_y + 5 * scale,
                18 * scale,
                cloud_color
            )

        arcade.draw_text(
            f"Score: {self.score}",
            10,
            WINDOW_HEIGHT - 30,
            arcade.color.WHITE,
            18
        )

        arcade.draw_text(
            f"Level: {self.level}",
            WINDOW_WIDTH // 2 -40,
            WINDOW_HEIGHT -30,
            arcade.color.WHITE,
            18
        )

        arcade.draw_text(
            f"Lives: {self.lives}",
            WINDOW_WIDTH - 120,
            WINDOW_HEIGHT - 30,
            arcade.color.WHITE,
            18
        )

        arcade.draw_sprite(self.player_sprite)

        for bullet in self.bullets:
            arcade.draw_lbwh_rectangle_filled(
                bullet[0],
                bullet[1],
                6,
                15,
                arcade.color.PURPLE
            )

        for enemy in self.enemies:
            arcade.draw_sprite(enemy[2])

        for bullet in self.enemy_bullets:
            arcade.draw_lbwh_rectangle_filled(
                bullet[0] -3,
                bullet[1] - 7.5,
                6,
                15,
                arcade.color.ORANGE
            )

        if self.game_won:
            arcade.draw_text(
                "You Win!",
                300,
                WINDOW_HEIGHT // 2,
                arcade.color.DARK_BLUE,
                36
            )
            arcade.draw_text(
                "Press R to restart",
                285,
                WINDOW_HEIGHT // 2 - 50,
                arcade.color.WHITE,
                18
            )

        if self.game_over:
            arcade.draw_text(
                "Game Over",
                280,
                WINDOW_HEIGHT // 2,
                arcade.color.RED,
                36
            )
            arcade.draw_text(
                "Press R to restart",
                285,
                WINDOW_HEIGHT // 2 - 50,
                arcade.color.WHITE,
                18
            )

    def on_update(self, delta_time):
        if self.game_won or self.game_over:
            return

        if self.enemies:
            self.enemy_shot_timer -= delta_time

            if self.enemy_shot_timer <= 0:
                shooter = random.choice(self.enemies)
                self.enemy_bullets.append([shooter[0], shooter[1] - 20])
                self.enemy_shot_timer = random.uniform(0.5, 1.2)

        if self.left_pressed:
            self.player_x -= PLAYER_SPEED * delta_time

        if self.right_pressed:
            self.player_x += PLAYER_SPEED * delta_time

        self.player_x = max(25, min(WINDOW_WIDTH - 25, self.player_x))

        if self.enemies:
            for enemy in self.enemies:
                enemy[0] += self.enemy_speed * self.enemy_direction * delta_time
                enemy[2].center_x = enemy[0]
                enemy[2].center_y = enemy[1]
            
            leftmost_enemy = min(enemy[0] for enemy in self.enemies)
            rightmost_enemy = max(enemy[0] for enemy in self.enemies)

            if leftmost_enemy <= 20 or rightmost_enemy >= WINDOW_WIDTH - 20:
                self.enemy_direction *= -1

                for enemy in self.enemies:
                    enemy[1] -= 20
                    enemy[2].center_x = enemy[0]
                    enemy[2].center_y = enemy[1]

                if any(enemy[1] <= 80 for enemy in self.enemies):
                    self.game_over = True

        self.player_sprite.center_x = self.player_x

        for bullet in self.bullets:
            bullet[1] += BULLET_SPEED * delta_time

        remaining_bullets = []

        for bullet in self.bullets:
            hit_enemy = None

            for enemy in self.enemies:
                if (
                    abs(bullet[0] - enemy[0]) < 23
                    and abs(bullet[1] - enemy[1]) < 22
                ):
                    hit_enemy = enemy
                    break

            if hit_enemy is not None:
                self.enemies.remove(hit_enemy)
                self.score += 10
            elif bullet[1] < WINDOW_HEIGHT:
                remaining_bullets.append(bullet)

        self.bullets = remaining_bullets

        remaining_enemy_bullets = []

        for bullet in self.enemy_bullets:
            bullet[1] -= ENEMY_BULLET_SPEED * delta_time

            bullet_hits_player = (
                abs(bullet[0] - self.player_x) < 20
                and 25 < bullet[1] < 85
            )

            if bullet_hits_player:
                self.lives -= 1
                self.player_x = WINDOW_WIDTH // 2
                self.enemy_bullets.clear()

                if self.lives <= 0:
                    self.game_over = True

            elif bullet[1] > 0:
                remaining_enemy_bullets.append(bullet)

        self.enemy_bullets = remaining_enemy_bullets

        if not self.enemies:
            if self.level < MAX_LEVEL:
                self.level += 1
                self.create_enemies()
                self.bullets.clear()
                self.enemy_bullets.clear()
            else: 
                self.game_won = True

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.R and (self.game_over or self.game_won):
            self.setup()
            return
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.SPACE:
            self.bullets.append([self.player_x, 90])

    def on_key_release(self, key, key_modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False



    def create_enemies(self):
        self.enemies = []
        self.enemy_direction = 1
        self.enemy_shot_timer = 1.0
        self.enemy_speed = ENEMY_SPEED + (self.level - 1) * 30

        rows = 2 + self.level
        columns = 6 + self.level

        for row in range(rows):
            for column in range(columns):
                enemy_x = 100 + column * 80
                enemy_y = WINDOW_HEIGHT - 100 - row * 60 
                enemy_sprite = arcade.Sprite(
                    ":resources:images/space_shooter/meteorGrey_small2.png",
                    scale=1.2
                )
                enemy_sprite.center_x = enemy_x
                enemy_sprite.center_y = enemy_y

                self.enemies.append([enemy_x, enemy_y, enemy_sprite])



def main():
    game = Game()
    game.setup()
    arcade.run()



if __name__ == "__main__":
    main()