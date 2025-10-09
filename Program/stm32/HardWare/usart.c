#include "stm32f10x.h"                  // Device header
#include "Delay.h"
#include "stdio.h"
#include "math.h"
#include "stdarg.h"
#include "string.h"
uint8_t Serial_RxPaket[100]={0x02};
uint8_t Serial_RxFlag;
void Serial_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStructure;
	NVIC_InitTypeDef NVIC_InitStructure;
	USART_InitTypeDef USART_InitStructure;
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA,ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_USART1,ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_AFIO,ENABLE);
	GPIO_InitStructure.GPIO_Mode=GPIO_Mode_AF_OD;
	GPIO_InitStructure.GPIO_Pin=GPIO_Pin_9;	//PA9是发送，PA10是接受
	GPIO_InitStructure.GPIO_Speed=GPIO_Speed_50MHz;
	GPIO_Init(GPIOA,&GPIO_InitStructure);
	GPIO_InitStructure.GPIO_Mode=GPIO_Mode_IPU;
	GPIO_InitStructure.GPIO_Pin=GPIO_Pin_10;	//PA9是发送，PA10是接受
	GPIO_Init(GPIOA,&GPIO_InitStructure);
	
	USART_InitStructure.USART_BaudRate=115200;
	USART_InitStructure.USART_HardwareFlowControl=USART_HardwareFlowControl_None;
	USART_InitStructure.USART_Mode=USART_Mode_Tx|USART_Mode_Rx;
	USART_InitStructure.USART_Parity= USART_Parity_No;
	USART_InitStructure.USART_StopBits=USART_StopBits_1 ;
	USART_InitStructure.USART_WordLength=USART_WordLength_8b;
	USART_Init(USART1,&USART_InitStructure);
	USART_Cmd(USART1,ENABLE);
	/*接受中断*/
	USART_ITConfig(USART1,USART_IT_RXNE,ENABLE);//相当于 EXTI 中断
	
	
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);

	NVIC_InitStructure.NVIC_IRQChannel=USART1_IRQn;
	NVIC_InitStructure.NVIC_IRQChannelCmd=ENABLE;
	NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority=2;
	NVIC_InitStructure.NVIC_IRQChannelSubPriority=2;
	NVIC_Init(&NVIC_InitStructure);
}

void Serial_SendByte(uint8_t Byte)
{
	USART_SendData(USART1,Byte);
	while(USART_GetFlagStatus(USART1,USART_FLAG_TXE)==RESET);
}
void Serial_SendString(char *string)
{
	uint16_t i;
	for(i=0;string[i]!='\0';i++)
	{
		Serial_SendByte(string[i]);
	}
}

void Serial_SendArray(uint8_t *Array,uint16_t Length)
{
	uint16_t i;
	for(i=0;i<Length;i++)
	{
		Serial_SendByte(Array[i]);
	}
}

void Serial_printf(char *fomat,...)
{
	char string[100];
	va_list arg;
	va_start(arg,fomat);
	vsprintf(string,fomat,arg);
	Serial_SendString(string);
}
/*16进制数据包格式为:0xAA 长度 .... 0x55*/
void USART1_IRQHandler(void)
{
	static uint8_t RxState=0;
	static uint8_t pRxPaket=0;
	if(USART_GetFlagStatus(USART1,USART_IT_RXNE)==SET)
	{
		uint8_t RxData=USART_ReceiveData(USART1);
		if(RxState==0)
		{
			if(RxData==0xAA)
			{
				RxState=1;
				pRxPaket=0;
			}
		}
		else if(RxState==1)
		{	
			Serial_RxPaket[pRxPaket]=RxData;
			pRxPaket++;
			if(pRxPaket==Serial_RxPaket[0])
			{
				RxState=2;
			}
		}
		else if(RxState==2)
		{
			if(RxData==0x55)
			{
				RxState=0;
				Serial_RxFlag=1;
			}
		}
		USART_ClearITPendingBit(USART1,USART_IT_RXNE);
	}
}

uint16_t Serial_Ro(uint8_t Hight,uint8_t Low)
{
	uint16_t val = Hight<<8|Low;
	return val;
}


