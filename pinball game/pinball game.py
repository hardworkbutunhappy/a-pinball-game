'''a pinball game'''
#if any bugs are discovered,repairing is welcomed
import pygame
import math
import random


class PinballGame:
    def __init__(self):
        '''initialize the game'''
        pygame.init()
        self.clock=pygame.time.Clock()
        self.screen_size=adapt_to_the_screen()
        self.screen=pygame.display.set_mode(self.screen_size,pygame.DOUBLEBUF)
        pygame.display.set_caption("PinballGame")
        self.settings=Settings(self)
        self.ball=Ball(self)
        self.block=Blocks(self)
        self.leftblock=LeftBlock(self)
        self.rightblock=RightBlock(self)
        self.situation_control=SituationControl(self)    
        #the follows are creating first screen
        self.leftblock.check_leftblock_collision()
        self.rightblock.check_rightblock_collision()
        self.ball.update_ball_position()

   

    def run_game(self):
        '''The main event of the game'''
        running=True
        reset_game=False

        #The main loop of the game
        while running:          
            for event in pygame.event.get():
                self.situation_control.start_stop_control(event)
                if event.type==pygame.QUIT:    
                    running=False
                if event.type==pygame.KEYDOWN and event.key==self.settings.reset_game_button:
                    reset_game=True
            keys=pygame.key.get_pressed()
            pygame.display.flip()
            self.clock.tick(self.settings.clock_tick)   
            #the pause and the start
            if self.situation_control.situation: 
                self.update_elements(keys)
            #controls the reset
            if reset_game:
                self.reset_elements(keys)
                reset_game=False

        #After the loop ends,exit the game
        pygame.quit()

    def update_elements(self,keys):
        '''all major events'''
        self.screen.fill(self.settings.background_color)
        self.ball.ball_screen_collision()
        self.ball.update_ball_position()
        leftblock_speed=self.leftblock.leftblock_move(keys)
        rightblock_speed=self.rightblock.rightblock_move(keys)
        self.ball.rotation_of_the_ball(leftblock_speed,rightblock_speed)
        self.leftblock.check_leftblock_collision()
        self.rightblock.check_rightblock_collision()


    def reset_elements(self,keys):
        '''all reset events'''
        self.situation_control.situation=False
        self.ball.reset_ball_pos()
        self.leftblock.y=reset_positions(self,"block")-self.block.height/2
        self.rightblock.y=reset_positions(self,"block")-self.block.height/2
        self.update_elements(keys)


class Settings:
    def __init__(self,ai):
        '''game settings'''
        self.ai=ai
        #the main settings
        self.clock_tick=60  #set the frame rate in 60
        self.background_color=(0,0,0)   #set a black background
        self.reset_game_button=pygame.K_r   #set R key for reset game
        self.pause_and_start=pygame.K_SPACE   #set SPACE key for pause and start


        #the ball settings
        self.ball_color=(255,255,255)   #set a white ball  
        self.ball_x_initial_position=self.ai.screen_size[0]/2   #set ball x inintal postion
        self.ball_y_initial_position=self.ai.screen_size[1]/2   #set ball y inintal postion
        self.ball_radius=self.ai.screen_size[1]/60  #set ball radius
        self.ball_speed=self.ai.screen_size[0]/200  #set ball speed


        #the block settings
        self.blocks_color=(192,192,192)  #set light gray blocks
        self.blocks_width=self.ai.screen_size[1]/60  #set width
        self.blocks_height=self.ai.screen_size[1]/8  #set height
        self.blocks_acceleration=self.ai.screen_size[0]/5000   #set accleration
        self.blocks_inital_y_pos=self.ai.screen_size[1]/2-self.blocks_height/2   #set block x inintal postion

        #the leftblock settings
        self.leftblock_up=pygame.K_w   #set W key for leftblock up
        self.leftblock_down=pygame.K_s  #set S key for leftblock down

        #the rightblock settings
        self.rightblock_up=pygame.K_UP  #set UP key for rightblock up
        self.rightblock_down=pygame.K_DOWN   #set DOWN key for rightblock down

        
def adapt_to_the_screen():
    '''adaptive screen size'''
    #you can also change the numbers in screen_size.txt to change game screen size
    try:
        with open('./screen_size.txt','r') as f:
            screen_width=int(f.readline())
            screen_hight=int(f.readline())
            return (screen_width*0.7,screen_hight*0.7)  #the screen size is 70% of the monitor
    except (FileNotFoundError,ValueError):  
        screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN).get_size()  #get screen size by creating a temporary fullscreen
        pygame.quit()
        with open('./screen_size.txt','w') as f:    #store the screen size in screen_size.txt
            for i in screen:
                f.write(f'{i}\n')
        return adapt_to_the_screen()


class SituationControl:
    def __init__(self,ai):
        '''main program state control'''
        self.ai=ai
        self.situation=False    #game initial state(pause)
        self.game_over=False

    def start_stop_control(self,event):
        '''for game pause and start'''
        if event.type==pygame.KEYDOWN and event.key==self.ai.settings.pause_and_start:
            if not self.game_over:
                self.situation=not self.situation
    

def reset_positions(ai,things):
    '''for all objects reset'''
    y=ai.screen_size[1]/2
    x=ai.screen_size[0]/2
    if things=="ball":
        return x,y
    elif things=="block":
        return y
    else:   #prevent reset failure
        class ObjectError(Exception):   
            pass
        raise ObjectError('unexpected object')


class Ball:
    def __init__(self,ai):
        '''about the ball'''
        self.ai=ai
        self.color=self.ai.settings.ball_color    
        self.center_x=self.ai.settings.ball_x_initial_position
        self.center_y=self.ai.settings.ball_y_initial_position
        self.radius=self.ai.settings.ball_radius   
        self.speed=self.ai.settings.ball_speed    
        self.dir_angle=random.choice([1,-1])*random.randint(15,75)/180*math.pi  #random ball angle
        self.conversion_factor=0.03   

    @staticmethod
    def ball_rect_collision(center,radius,rect):
        """detect collisions between ball and blocks"""
        rect_left, rect_top=rect.topleft
        rect_right, rect_bottom=rect.bottomright
        #calculate the closest point on the block to the center of the ball
        closest_x = max(rect_left, min(center[0], rect_right))
        closest_y = max(rect_top, min(center[1], rect_bottom))
        #calculate the square of the distance
        distance_squared = (center[0] - closest_x) ** 2 + (center[1] - closest_y) ** 2
        #if the distance is less than or equal to the radius, a collision occurs
        return distance_squared <= radius ** 2

    def update_ball_position(self):
        '''the movement of the ball'''
        self.x_speed=math.cos(self.dir_angle)*self.speed
        self.y_speed=math.sin(self.dir_angle)*self.speed
        self.center_x=int(self.center_x+self.x_speed)
        self.center_y=int(self.center_y+self.y_speed)
        self.center=(self.center_x,self.center_y)
        #the ball's bouncing up, down, left and right
        if self.center_y-self.radius<=0:
            self.dir_angle=-self.dir_angle
            self.center_y=self.radius
        elif self.center_y+self.radius>=self.ai.screen_size[1]:
            self.dir_angle=-self.dir_angle
            self.center_y=self.ai.screen_size[1]-self.radius
        if Ball.ball_rect_collision(self.center,self.radius,self.ai.leftblock.rect):
            self.dir_angle=math.pi-self.dir_angle
            self.center_x=self.radius+self.ai.leftblock.width+1
        elif Ball.ball_rect_collision(self.center,self.radius,self.ai.rightblock.rect):
            self.dir_angle=math.pi-self.dir_angle
            self.center_x=self.ai.screen_size[0]-self.radius-self.ai.rightblock.width-1
        pygame.draw.circle(self.ai.screen,self.color,self.center,self.radius)

    def rotation_of_the_ball(self,leftblock_speed,rightblock_speed):
        '''adjust the angle of the ball's rebound based on the speed of the paddle'''
        block_speed=0
        if leftblock_speed!=None:
            block_speed=leftblock_speed
        elif rightblock_speed!=None:
            block_speed=rightblock_speed
        self.dir_angle=self.dir_angle+block_speed*self.conversion_factor

    def reset_ball_pos(self):
        '''reset ball position'''
        self.center_x,self.center_y=reset_positions(self.ai,"ball")
       
    def ball_screen_collision(self):
        '''deal with the ball and screen collision'''
        if self.center_x-self.radius<=0 or self.center_x+self.radius>=self.ai.screen_size[0]:
            self.ai.situation_control.situation=False
            self.ai.situation_control.game_over=True
            return True
        else:
            return False

       
class Blocks:
    def __init__(self,ai):
        '''about all the blocks'''
        self.ai=ai
        self.screen=ai.screen
        self.screen_size=ai.screen_size
        self.color=self.ai.settings.blocks_color   
        self.width=self.ai.settings.blocks_width
        self.height=self.ai.settings.blocks_height   
        self.acceleration=self.ai.settings.blocks_acceleration    
        self.y=self.ai.settings.blocks_inital_y_pos    
        self.up_move=False    
        self.down_move=False
        self.speed=0    #inital speed

            
class LeftBlock(Blocks):
    def __init__(self,ai):
        '''about the leftblock'''
        super().__init__(ai)
        self.x=0
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
    
    def check_leftblock_collision(self):
        '''restrict the movement range of the left block'''
        if self.y<=0:
            self.y=0
        if self.y+self.height>=self.screen_size[1]:
            self.y=self.screen_size[1]-self.height
        pygame.draw.rect(self.screen,self.color,self.rect)

    def leftblock_move(self,keys):
        '''movement of leftblock'''
        if keys[self.ai.settings.leftblock_down]:
            self.speed+=self.acceleration
        if keys[self.ai.settings.leftblock_up]:
            self.speed-=self.acceleration
        if not keys[self.ai.settings.leftblock_down] and not keys[self.ai.settings.leftblock_up]:
            self.speed*=(1-self.acceleration)
        self.y+=self.speed
        self.rect.topright=(int(self.x+self.width),int(self.y))
        pygame.draw.rect(self.screen,self.color,self.rect)
        if Ball.ball_rect_collision(self.ai.ball.center, self.ai.ball.radius, self.rect):
            return self.speed 
        else:
            return None


class RightBlock(Blocks): 
    def __init__(self,ai):
        '''about the rightblock'''
        super().__init__(ai)
        self.x=self.screen_size[0]-self.width
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
    
    def check_rightblock_collision(self):
        '''restrict the movement range of the rightblock'''
        if self.y<=0:
            self.y=0
        if self.y+self.height>=self.screen_size[1]:
            self.y=self.screen_size[1]-self.height
        pygame.draw.rect(self.screen,self.color,self.rect)

    def rightblock_move(self,keys):
        '''movement of rightblock'''
        if keys[self.ai.settings.rightblock_down]:
            self.speed+=self.acceleration
        if keys[self.ai.settings.rightblock_up]:
            self.speed-=self.acceleration
        if not keys[self.ai.settings.rightblock_down] and not keys[self.ai.settings.rightblock_up]:
            self.speed*=1-self.acceleration
        self.y+=self.speed
        self.rect.topleft=(int(self.x),int(self.y))
        pygame.draw.rect(self.screen,self.color,self.rect)
        if Ball.ball_rect_collision(self.ai.ball.center, self.ai.ball.radius, self.rect):
            return self.speed
        else:
            return None


if __name__=="__main__":
    ai=PinballGame()
    ai.run_game()