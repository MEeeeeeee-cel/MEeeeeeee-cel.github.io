#include "stm32f10x.h"                  // Device header
#include "Delay.h"
#include "OLED.h"
#include "stdio.h"
#include "TIM.h"
#include "LED.h"
#include "DS18B20.h"
int16_t temp;
int main()
{
	LED_Init();
	PWM_INIT();
	OLED_Init();
	MOTOR_INIT();
	while(DS18B20_INIT()){OLED_ShowString(1,1,"DS18B20 ERROR");Delay_s(1);}
	OLED_ShowString(1,1,"DS18B20 READY");
	
	LED_ON();
	
	while(1)
	{
		temp = DS18B20_GET_TEMPERATURE();
		OLED_ShowSignedNum(2,1,temp,3);
		if(temp<25 && temp>=0)
		{
			temp=0;
		}
		MOTOR_SET_SPEED(temp*2);
		Delay_ms(10);
		
	}
}	


