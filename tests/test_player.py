import pytest
import pygame
from src.main import Player, Laser

@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    yield
    pygame.quit()

@pytest.fixture
def player_instance():
    return  Player(pygame.sprite.Group(), 
        pygame.Surface((1,1)),
        {
            'laser surface': pygame.Surface((1,1)), 
            'laser sound': pygame.mixer.Sound(buffer=b""), # Sonido vacío
            'laser sprite': pygame.sprite.Group()},
        pygame.Surface((100,100)))

def test_player_initial_life(player_instance):
    assert player_instance.life == 1000

def test_player_ammo_decrease(player_instance):
    initial_ammo = player_instance.ammo
    player_instance.ammo -= 1 
    assert player_instance.ammo == initial_ammo - 1

def test_player_ammo_limit(player_instance):   
    assert player_instance.ammo == 15
    player_instance.ammo -= 5
    assert player_instance.ammo == 10

def test_player_movement_logic(player_instance):
    assert player_instance.direction.x == 0
    assert player_instance.direction.y == 0

def test_laser_out_of_bounds():
    group = pygame.sprite.Group()
    surf = pygame.Surface((5, 5))
    laser = Laser(group, surf, (500, -10))
    
    laser.update(0.016)
    assert len(group) == 0
