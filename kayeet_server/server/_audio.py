"""
audio.pyw
02.05.2024

system to play audio samples at good times

Author:
melektron
"""

import pygame
import time as t
import asyncio
import random 
from typing import Sequence

class Audio:
    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()

        self._crash = pygame.mixer.Sound("sound/acoustic-classic-crash-2.wav")
        self._snap = pygame.mixer.Sound("sound/acoustic-snap-one-shor_90bpm_amplified.wav")
        self._plop = pygame.mixer.Sound("sound/bubble_Gsharp_major_amplified.wav")
        self._connect_loopable = pygame.mixer.Sound("sound/connect_loopable.wav")
        self._question_loop_1 = pygame.mixer.Sound("sound/question_loop_1.wav")
        self._question_loop_2 = pygame.mixer.Sound("sound/question_loop_2.wav")
        self._question_loop_3 = pygame.mixer.Sound("sound/question_loop_3.wav")
        self._question_loop: asyncio.Task | None = None

    def quiet(self) -> None:
        self._crash.stop()
        self._connect_loopable.stop()
        self._question_loop_1.stop()
        self._question_loop_2.stop()
        self._question_loop_3.stop()
    
    def start_connect_sound(self) -> None:
        self._connect_loopable.play(loops=-1)   # loop indefinitely
        #self._connect_loopable.set_volume(0.8)
    
    async def end_connect_sound(self) -> None:
        self._connect_loopable.fadeout(1000)
        await asyncio.sleep(1)
    
    def start_question_sound(self) -> None:
        # stop task if running
        if self._question_loop is not None:
            if not self._question_loop.done():
                self._question_loop.cancel()
            self._question_loop = None
        # stop question sounds just in case
        self._question_loop_1.stop()
        self._question_loop_2.stop()
        self._question_loop_3.stop()

        async def play_random(possible: Sequence[pygame.mixer.Sound]) -> None:
            sound = random.sample(possible, 1)[0]
            sound.play()
            #sound.set_volume(0.8)
            await asyncio.sleep(sound.get_length())
        
        async def run_loop() -> None:
            # always start with sound 1 or 2
            await play_random((
                self._question_loop_1, 
                self._question_loop_2
            ))
            # play random sounds in loop
            while True:
                await play_random((
                    self._question_loop_1, 
                    self._question_loop_2, 
                    self._question_loop_3,
                ))
        self._question_loop = asyncio.create_task(run_loop())
    
    async def end_question_sound(self) -> None:
        # stop task if running
        if self._question_loop is not None:
            if not self._question_loop.done():
                self._question_loop.cancel()
            self._question_loop = None
        
        # fade out whatever soundtrack may be running while playing crash at the same time
        self._question_loop_1.fadeout(1000)
        self._question_loop_2.fadeout(1000)
        self._question_loop_3.fadeout(1000)
        self._crash.play()
        await asyncio.sleep(1)
        self._crash.fadeout(500)
        await asyncio.sleep(0.5)
    
    def play_answer_submitted_effect(self) -> None:
        snd = random.sample((self._plop, self._snap), 1)[0]
        snd.play()
        #snd.set_volume(1.0)


AUDIO = Audio()

async def _tests() -> None:
    #a.start_connect_sound()
    #await asyncio.sleep(30)
    #await a.end_connect_sound()
    #await asyncio.sleep(1)
    AUDIO.start_question_sound()
    await asyncio.sleep(3)
    for _ in range(20):
        #pygame.mixer.Sound("sound/bubble_Gsharp_major.wav").play()
        AUDIO.play_answer_submitted_effect()
        await asyncio.sleep(random.randint(1, 5) * 0.1)
    await AUDIO.end_question_sound()

if __name__ == "__main__":
    asyncio.run(_tests())
