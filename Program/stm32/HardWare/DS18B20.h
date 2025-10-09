#ifndef __DS18B20_H
#define __DS18B20_H
#include "stdint.h"
#include "sys.h"
//IO��������
#define DS18B20_IO_IN()  {GPIOA->CRH&=0XFFFFFFF0;GPIOA->CRH|=8<<0;}
#define DS18B20_IO_OUT() {GPIOA->CRH&=0XFFFFFFF0;GPIOA->CRH|=3<<0;}

//IO��������											   
#define	DS18B20_DQ_OUT PAout(8) //���ݶ˿�	PA0 
#define	DS18B20_DQ_IN  PAin(8)  //���ݶ˿�	PA0 

#define DS18B20_GPIO_PORT		GPIOA
#define DS18B20_GPIO_PIN		GPIO_Pin_8
#define DS18B20_GPIO_CLK   	RCC_APB2Periph_GPIOA


void DS18B20_RST(void);
uint8_t DS18B20_CHECK(void);
uint8_t DS18B20_READ_BIT(void);
uint8_t DS18B20_READ_BYTE(void);
void DS18B20_WRITE_BYTE(uint8_t byte);

void DS18B20_START(void);
uint8_t DS18B20_INIT(void);
int16_t DS18B20_GET_TEMPERATURE(void);

#endif
