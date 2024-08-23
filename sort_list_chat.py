import pygame
import pygame_gui
from pygame_gui.elements import UIButton
from pygame_gui.elements.ui_panel import UIPanel


class DraggableButton(UIButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_dragging = False
        self.original_position = self.relative_rect.topleft

    def start_drag(self, mouse_pos):
        self.is_dragging = True
        self.original_position = self.relative_rect.topleft
        self.mouse_offset = (self.relative_rect.x - mouse_pos[0], self.relative_rect.y - mouse_pos[1])

    def drag(self, mouse_pos):
        if self.is_dragging:
            # Constrain movement to the Y-axis
            self.set_relative_position((self.original_position[0], mouse_pos[1] + self.mouse_offset[1]))

    def stop_drag(self):
        self.is_dragging = False
        self.set_relative_position(self.original_position)


class CustomScrollingWidget(UIPanel):
    def __init__(self, relative_rect, manager, button_names):
        super().__init__(relative_rect, manager=manager, starting_height=1)
        
        self.scroll_panel = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(0, 0, relative_rect.width, relative_rect.height),
            manager=manager,
            container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        self.buttons = []
        self.setup_buttons(button_names)
        self.manager = manager
        self.dragged_button = None

    def setup_buttons(self, button_names):
        button_height = 50
        for i, name in enumerate(button_names):
            button = DraggableButton(
                relative_rect=pygame.Rect(0, i * button_height, self.relative_rect.width-20, button_height),
                text=name,
                manager=self.ui_manager,
                container=self.scroll_panel
            )
            self.buttons.append(button)

    def update(self, time_delta):
        super().update(time_delta)

        if self.dragged_button:
            # Handle dragging
            mouse_pos = pygame.mouse.get_pos()
            self.dragged_button.drag(mouse_pos)
            
            # Check for reordering
            self.check_for_reorder()

    def check_for_reorder(self):
        if not self.dragged_button:
            return

        dragged_button_index = self.buttons.index(self.dragged_button)
        dragged_button_rect = self.dragged_button.rect

        for i, button in enumerate(self.buttons):
            if button is self.dragged_button:
                continue

            button_rect = button.rect

            if dragged_button_rect.colliderect(button_rect):
                if i < dragged_button_index and dragged_button_rect.top < button_rect.centery:
                    # Move dragged button up in the stack
                    self.shift_buttons(dragged_button_index, i)
                    break
                elif i > dragged_button_index and dragged_button_rect.bottom > button_rect.centery:
                    # Move dragged button down in the stack
                    self.shift_buttons(dragged_button_index, i)
                    break

    def shift_buttons(self, start_index, end_index):
        dragged_button = self.buttons[start_index]

        if start_index < end_index:
            # Moving down: Shift other buttons up
            for i in range(start_index, end_index):
                self.buttons[i] = self.buttons[i + 1]
        else:
            # Moving up: Shift other buttons down
            for i in range(start_index, end_index, -1):
                self.buttons[i] = self.buttons[i - 1]

        # Place the dragged button in its new position
        self.buttons[end_index] = dragged_button
        self.reorder_buttons()

    def reorder_buttons(self):
        for i, button in enumerate(self.buttons):
            button.set_relative_position((0, i * button.rect.height))
            # Update the original position for each button
            button.original_position = button.relative_rect.topleft

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                for button in self.buttons:
                    print(button.text)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                if button.rect.collidepoint(event.pos):
                    self.dragged_button = button
                    button.start_drag(event.pos)
                    break

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragged_button:
                self.dragged_button.stop_drag()
                self.dragged_button = None


def main():
    pygame.init()
    pygame.display.set_caption('Custom Scrolling Widget')
    window_surface = pygame.display.set_mode((400, 600))
    background = pygame.Surface((400, 600))
    background.fill(pygame.Color('#000000'))
    manager = pygame_gui.UIManager((400, 600))

    widget = CustomScrollingWidget(
        relative_rect=pygame.Rect(50, 50, 300, 500),
        manager=manager,
        button_names=[f'Button {i}' for i in range(20)]
    )

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            widget.handle_event(event)  # Handle events specifically for the widget
            manager.process_events(event)

        widget.update(time_delta)
        manager.update(time_delta)
        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()


if __name__ == '__main__':
    main()
