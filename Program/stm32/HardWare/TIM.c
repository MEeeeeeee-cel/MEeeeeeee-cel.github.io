#include "stm32f10x.h"                  // Device header
#include "LED.h"
#include "stdio.h"
#include "TIM.h"
#include <string.h>
void PWM_INIT(void)
{
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA,ENABLE);
	GPIO_InitTypeDef GPIO_InitStructure;
	GPIO_InitStructure.GPIO_Mode=GPIO_Mode_AF_PP;
	GPIO_InitStructure.GPIO_Pin=GPIO_Pin_2;
	GPIO_InitStructure.GPIO_Speed=GPIO_Speed_50MHz;
	GPIO_Init(GPIOA,&GPIO_InitStructure);
	
	TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure;
	TIM_OCInitTypeDef TIMOCInitstructure;
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2,ENABLE);
	TIM_TimeBaseStructure.TIM_ClockDivision = TIM_CKD_DIV1;
	TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up;//计数方式（向上计数）
	TIM_TimeBaseStructure.TIM_Period = 100 - 1;//计数值ARR
	TIM_TimeBaseStructure.TIM_Prescaler = (100 - 1);//预分频PSC
	TIM_TimeBaseInit(TIM2,&TIM_TimeBaseStructure);
	
	TIM_OCStructInit(&TIMOCInitstructure);
	TIMOCInitstructure.TIM_OCMode = TIM_OCMode_PWM1;
	TIMOCInitstructure.TIM_OCPolarity = TIM_OCPolarity_High;
	TIMOCInitstructure.TIM_OutputState = TIM_OutputState_Enable;
	TIMOCInitstructure.TIM_Pulse = 0;			//CCR的值
	TIM_OC3Init(TIM2,&TIMOCInitstructure);
	
	TIM_Cmd(TIM2,ENABLE);
}

void MOTOR_INIT(void)
{
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA,ENABLE);
	GPIO_InitTypeDef GPIO_InitStructure;
	GPIO_InitStructure.GPIO_Mode=GPIO_Mode_Out_PP;
	GPIO_InitStructure.GPIO_Pin=GPIO_Pin_4 | GPIO_Pin_5;
	GPIO_InitStructure.GPIO_Speed=GPIO_Speed_50MHz;
	GPIO_Init(GPIOA,&GPIO_InitStructure);
}

void MOTOR_SET_SPEED(int SPEED)
{
	if(SPEED>=0)
	{
		GPIO_SetBits(GPIOA, GPIO_Pin_4);
		GPIO_ResetBits(GPIOA, GPIO_Pin_5);
		TIM_SetCompare3(TIM2,SPEED);
	}
	else
	{
		GPIO_SetBits(GPIOA, GPIO_Pin_5);
		GPIO_ResetBits(GPIOA, GPIO_Pin_4);
		TIM_SetCompare3(TIM2,-SPEED);
	}
}
