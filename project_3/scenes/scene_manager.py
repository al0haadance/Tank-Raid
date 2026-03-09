class SceneManager:
    def __init__(self, scene):
        self.scene = scene

    def change_scene(self, new_scene):
        self.scene = new_scene

    def handle_events(self, event):
        self.scene.handle_events(event)

    def update(self):
        self.scene.update()

    def draw(self, screen):
        self.scene.draw(screen)
