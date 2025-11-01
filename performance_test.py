#!/usr/bin/env python3
"""
Performance testing tool for Geo Dash.
Measures FPS and identifies bottlenecks.
"""

import pygame
import time
import sys

# Must initialize pygame before importing game modules
pygame.init()

from game.config import *
from game.assets import asset_manager
from game.player import Player
from game.obstacles import ObstacleGenerator
from game.renderer import Renderer


class PerformanceTester:
    """Test game performance and identify bottlenecks."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Geo Dash - Performance Test")
        self.clock = pygame.time.Clock()
        
        # Game objects
        self.player = Player(PLAYER_START_X, GROUND_Y, character_name="bloemetje.svg")
        self.obstacle_generator = ObstacleGenerator()
        self.renderer = Renderer(self.screen)
        
        # Performance metrics
        self.frame_times = []
        self.draw_times = []
        self.update_times = []
        
    def run_test(self, duration_seconds=10):
        """Run performance test for specified duration."""
        print(f"\n{'='*60}")
        print(f"Running performance test for {duration_seconds} seconds...")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        frame_count = 0
        
        running = True
        while running and (time.time() - start_time) < duration_seconds:
            frame_start = time.perf_counter()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
            
            # Update
            update_start = time.perf_counter()
            self.player.update()
            self.obstacle_generator.update()
            update_time = (time.perf_counter() - update_start) * 1000
            self.update_times.append(update_time)
            
            # Draw
            draw_start = time.perf_counter()
            self.renderer.draw_background()
            self.renderer.draw_ground()
            self.obstacle_generator.draw(self.screen)
            self.player.draw(self.screen)
            
            # Draw FPS counter
            fps = self.clock.get_fps()
            font = pygame.font.Font(None, 36)
            fps_text = font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
            self.screen.blit(fps_text, (10, 10))
            
            pygame.display.flip()
            draw_time = (time.perf_counter() - draw_start) * 1000
            self.draw_times.append(draw_time)
            
            # Frame timing
            frame_time = (time.perf_counter() - frame_start) * 1000
            self.frame_times.append(frame_time)
            
            self.clock.tick(FPS)
            frame_count += 1
        
        # Calculate statistics
        elapsed = time.time() - start_time
        avg_fps = frame_count / elapsed
        
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        max_frame_time = max(self.frame_times)
        min_frame_time = min(self.frame_times)
        
        avg_draw_time = sum(self.draw_times) / len(self.draw_times)
        avg_update_time = sum(self.update_times) / len(self.update_times)
        
        # Print results
        print(f"\n{'='*60}")
        print("PERFORMANCE TEST RESULTS")
        print(f"{'='*60}\n")
        
        print(f"📊 Overall Statistics:")
        print(f"  Duration: {elapsed:.2f}s")
        print(f"  Total Frames: {frame_count}")
        print(f"  Average FPS: {avg_fps:.1f}")
        print(f"  Target FPS: {FPS}")
        print(f"  FPS Achievement: {(avg_fps/FPS)*100:.1f}%")
        
        print(f"\n⏱️  Timing Breakdown:")
        print(f"  Frame Time (avg): {avg_frame_time:.2f}ms")
        print(f"  Frame Time (min): {min_frame_time:.2f}ms")
        print(f"  Frame Time (max): {max_frame_time:.2f}ms")
        print(f"  Target Frame Time: {(1000/FPS):.2f}ms")
        
        print(f"\n🎨 Draw Performance:")
        print(f"  Average Draw Time: {avg_draw_time:.2f}ms")
        print(f"  Draw % of Frame: {(avg_draw_time/avg_frame_time)*100:.1f}%")
        
        print(f"\n🔄 Update Performance:")
        print(f"  Average Update Time: {avg_update_time:.2f}ms")
        print(f"  Update % of Frame: {(avg_update_time/avg_frame_time)*100:.1f}%")
        
        print(f"\n💡 Recommendations:")
        if avg_fps < FPS * 0.95:
            print(f"  ⚠️  FPS is below target ({avg_fps:.1f} vs {FPS})")
            if avg_draw_time > (1000/FPS) * 0.5:
                print(f"  → Draw calls are expensive ({avg_draw_time:.2f}ms)")
                print(f"     Consider: dirty rect rendering, sprite batching")
            if avg_update_time > (1000/FPS) * 0.3:
                print(f"  → Update logic is expensive ({avg_update_time:.2f}ms)")
                print(f"     Consider: object pooling, spatial partitioning")
        else:
            print(f"  ✅ Performance is good!")
            print(f"  → Average FPS: {avg_fps:.1f}")
            print(f"  → Frame time budget used: {(avg_frame_time/(1000/FPS))*100:.1f}%")
        
        print(f"\n{'='*60}\n")


def main():
    """Run performance test."""
    tester = PerformanceTester()
    
    # Run test (default 10 seconds, or specify duration)
    duration = 10
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print(f"Invalid duration: {sys.argv[1]}, using default 10s")
    
    tester.run_test(duration)
    pygame.quit()


if __name__ == "__main__":
    main()
