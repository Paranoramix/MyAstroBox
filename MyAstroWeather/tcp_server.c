/*
    C socket server example, handles multiple clients using threads
    Compile
    gcc tcp_server.c -lpthread -lbcm2835 -lwiringPi -lm -o myAstroWeather
*/
#define BCM2835_NO_DELAY_COMPATIBILITY
#include <bcm2835.h>
#include <wiringPi.h>
 
#include<stdio.h>
#include<string.h>    //strlen
#include<stdlib.h>    //strlen
#include<sys/socket.h>
#include<arpa/inet.h> //inet_addr
#include<unistd.h>    //write
#include<pthread.h> //for threading , link with lpthread
#include <math.h>
#include <stdbool.h>
#include <errno.h>

// Definition constants for TCP socket server
#define TCP_SERVER_PORT 1610

// Definition constants for TX20 sensor
#define TX20_BIT_LENGTH 1200											// Length for each TX20 bit data
#define TX20_DATA_PIN 0														// TX20 data pin input (wiringPi mapping) - GPIO 17
#define TX20_COMMAND_PIN 3												// TX20 command pin output (wiringPi mapping) - GPIO 22

// Definition constants for MLX90614 sensor
#define MLX90614_BAUD_RATE 25000									// Baud rate for I²C bus.
#define MLX90614_SLAVE_ADDR 0x5a									// Slave address for I²C MLX90614 sensor.

// Definition constants for DHT22 sensor
#define DHT22_MAXTIMINGS 85
#define DHT22_DATA_PIN 7												// DHT22 data pin (wiringPi mapping) - GPIO 4

// Constants
const char* GET_DHT22_TEMPERATURE = "GET_DHT22_TEMPERATURE";
const char* GET_DHT22_RELATIVE_HUMIDITY = "GET_DHT22_RELATIVE_HUMIDITY";
const char* GET_TX20_WIND_SPEED = "GET_TX20_WIND_SPEED";
const char* GET_TX20_WIND_DIRECTION = "GET_TX20_WIND_DIRECTION";
const char* GET_MLX90614_AMBIANT_TEMPERATURE = "GET_MLX90614_AMBIANT_TEMPERATURE";
const char* GET_MLX90614_IR_TEMPERATURE = "GET_MLX90614_IR_TEMPERATURE";
const char* GET_ALL_DATA_SENSORS = "GET_ALL_DATA_SENSORS";

// Variables globales
static volatile bool is_tx20_interrupt = false; 						// is_tx20_interrupt is a flag to treat only one interruption at the same time.
static volatile float tx20_wind_speed = 0.0; 								// TX20 wind_speed is the last measure of wind speed.
static volatile float tx20_wind_direction = 0.0;						// TX20 wind_direction is the last measure ont wind direction.
static volatile long tx20_last_update = 0.0;								// TX20 last update.
static double mlx90614_ambiant_temperature = 0.0;						// MLX90614 ambiant temperature.
static double mlx90614_infrared_temperature = 0.0;					// MLX90614 infrared temperature.
static volatile long mlx90614_last_update = 0.0;						// MLX90614 last update.
static volatile float dht22_temperature = 0.0;							// DHT22 temperature.
static volatile float dht22_humidity = 0.0;									// DHT22 relative humidity.
static volatile long dht22_last_update = 0.0;								// DHT22 last update.

// the thread function
void *connection_handler(void *);
void *read_sensors(void *);

// the interruption function for TX20.
void tx20_interrupt(void);

void init_mlx90614(void);
void init_tx20(void);
void init_dht22(void);

	/* digitalRead() and friends from wiringpi are defined as returning a value
	< 256. However, they are returned as int() types. This is a safety function */
static uint8_t sizecvt(const int read);
static int read_dht22_dat(void);
static void read_mlx90614(void);


 
int main(int argc , char *argv[]) {
	int socket_desc , client_sock , c;
	struct sockaddr_in server , client;
	
	printf("myAstroWeather TCP Server v0.1\nDevelopped by Gilles LEONIS (2016)\n\nhttps://github.com/Paranoramix/MyAstroBox\n\n");
	printf("This is the sensor controller to retrieve latest data from weather sensor.\n     - TX20: LaCie anemometer and wind direction\n     - DHT22: Relative Humidity and ambiant temperature\n     - MLX90614: Infrared temperature (used for cloud detection)\n\nData is updated every 5 seconds (about).\n\n");
	printf("usage: sudo ./myAstroWeather\n\n");
	
	// Initialisation for wiringPi gpio.
	if (wiringPiSetup () == -1) {
		exit(EXIT_FAILURE) ;
	} 
	
	if (setuid(getuid()) < 0) {
		perror("Dropping privileges failed\n");
		exit(EXIT_FAILURE);
	}

	init_mlx90614();
	init_tx20();
	init_dht22();
	
	//Create socket
	socket_desc = socket(AF_INET , SOCK_STREAM , 0);
	if (socket_desc == -1) {
			printf("Could not create socket");
	}
	//puts("Socket created");
	 
	//Prepare the sockaddr_in structure
	server.sin_family = AF_INET;
	server.sin_addr.s_addr = INADDR_ANY;
	server.sin_port = htons(TCP_SERVER_PORT);
	 
	//Bind
	if( bind(socket_desc,(struct sockaddr *)&server , sizeof(server)) < 0) {
			//print the error message
			perror("bind failed. Error");
			return 1;
	}
	//puts("bind done");
	 
	//Listen
	listen(socket_desc, 3);
	 
	//Accept and incoming connection
	//puts("Waiting for incoming connections...");
	c = sizeof(struct sockaddr_in);
	 
	 
	//Accept and incoming connection
	//puts("Waiting for incoming connections...");
	c = sizeof(struct sockaddr_in);
	pthread_t thread_id, sensor_thread;
	
	if (pthread_create(&sensor_thread, NULL, read_sensors, NULL) < 0) {
					perror("could not create sensor thread");
					return 1;
	}
	
	while( (client_sock = accept(socket_desc, (struct sockaddr *)&client, (socklen_t*)&c)) ) {
			//puts("Connection accepted");
			 
			if( pthread_create( &thread_id , NULL ,  connection_handler , (void*) &client_sock) < 0) {
					perror("could not create thread");
					return 1;
			}
			 
			//Now join the thread , so that we dont terminate before the thread
			//pthread_join( thread_id , NULL);
			//puts("Handler assigned");
	}
	 
	if (client_sock < 0) {
			perror("accept failed");
			return 1; 
	}
	 
	return 0;
}

/*
 * This will handle connection for each client
 * */
void *connection_handler(void *socket_desc) {
	//Get the socket descriptor
	int sock = *(int*)socket_desc;
	int read_size;
	char client_message[2000];
	char response[50];
	//Send some messages to the client
	//Receive a message from client
	while( (read_size = recv(sock , client_message , 2000 , 0)) > 0 ) {
		//end of string marker
	//	client_message[read_size] = '\0';
		
		//puts(client_message);
	 		
		// On traite la demande de l'utilisateur
		if (strcmp(client_message, GET_DHT22_TEMPERATURE) == 0) {
			sprintf(response, "GET_DHT22_TEMPERATURE     %.1f     %ld", dht22_temperature, (micros() - dht22_last_update));
			write(sock, response , strlen(response));
		}
		
		if (strcmp(client_message, GET_DHT22_RELATIVE_HUMIDITY) == 0) {
			sprintf(response, "GET_DHT22_RELATIVE_HUMIDITY     %.1f     %ld", dht22_humidity, (micros() - dht22_last_update));
			write(sock, response , strlen(response));
		}
		
		if (strcmp(client_message, GET_TX20_WIND_SPEED) == 0) {
			sprintf(response, "GET_TX20_WIND_SPEED     %.1f     %ld", tx20_wind_speed, (micros() - dht22_last_update));
			write(sock, response , strlen(response));
		}
			
		if (strcmp(client_message, GET_TX20_WIND_DIRECTION) == 0) {
			sprintf(response, "GET_TX20_WIND_DIRECTION     %.1f     %ld", tx20_wind_direction, (micros() - dht22_last_update));
			write(sock, response , strlen(response));
		}
		
		if (strcmp(client_message, GET_MLX90614_AMBIANT_TEMPERATURE) == 0) {
			sprintf(response, "GET_MLX90614_AMBIANT_TEMPERATURE     %.1f     %ld", mlx90614_ambiant_temperature, (micros() - dht22_last_update));
			write(sock, response , strlen(response));
		}
		
		if (strcmp(client_message, GET_MLX90614_IR_TEMPERATURE) == 0) {
			sprintf(response, "GET_MLX90614_IR_TEMPERATURE     %.1f     %ld", mlx90614_infrared_temperature, (micros() - dht22_last_update));
			write(sock, response , strlen(response));
		}
		
		if (strcmp(client_message, GET_ALL_DATA_SENSORS) == 0) {
			sprintf(response, "GET_ALL_DATA_SENSORS     %.1f     %.1f     %ld     %.1f     %.1f     %ld     %.1f     %.1f     %ld     %u     "
			, dht22_temperature, dht22_humidity, (micros() - dht22_last_update)
			, tx20_wind_speed, tx20_wind_direction, (micros() - tx20_last_update)
			, mlx90614_ambiant_temperature, mlx90614_infrared_temperature, (micros() - mlx90614_last_update), (unsigned) time(NULL));
		//	printf("%s %d\n", response, strlen(response));
			write(sock, response, strlen(response));
		}

		//clear the message buffer
		memset(client_message, 0, 2000); 
	}

	if(read_size == 0) {
			//puts("Client disconnected");
			fflush(stdout);
	} else if(read_size == -1) {
			perror("recv failed");
	}

	return 0;
} 

void *read_sensors(void *args) {
		time_t t = time(NULL);

	struct tm tm = *localtime(&t);
	int r = 5 - (tm.tm_sec % 5);
	delay(r * 1000);
	
	// Infinite loop to read sensors
	while(1) {
		time_t t = time(NULL);

		struct tm tm = *localtime(&t);
		int r = 5 - (tm.tm_sec % 5);
		//printf("tm_sec: %02d   reste: %d\n", tm.tm_sec, r);

		read_dht22_dat();

		// Reinitialization of the flag.
		is_tx20_interrupt = false;
		
		read_mlx90614();

		// TX20_COMMAND_PIN is written to LOW to request a new measure from anemometer
		digitalWrite(TX20_COMMAND_PIN, LOW);
		//printf("%d-%02d-%02d %02d:%02d:%02d\nTX20_WD: %04.2f    TX20_WS: %04.2f    MLX9_ST: %04.2f    MLX9_AT: %04.2f    DHT2_TE: %04.2f    DHT2_HU: %04.2f\n"
		//, tm.tm_year, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec, tx20_wind_direction, tx20_wind_speed, mlx90614_infrared_temperature, mlx90614_ambiant_temperature, dht22_temperature, dht22_humidity);
		delay(r * 1000 - 2000);
	}

	delay(1500);
}

void init_mlx90614(void) {
	bcm2835_init();
	bcm2835_i2c_begin();
	bcm2835_i2c_set_baudrate(MLX90614_BAUD_RATE);
	bcm2835_i2c_setSlaveAddress(MLX90614_SLAVE_ADDR);
	
	mlx90614_last_update = micros();
}

void init_tx20(void) {
		// initialize the mode for all GPIOs
	pinMode(TX20_DATA_PIN, INPUT);
	pinMode(TX20_COMMAND_PIN, OUTPUT);

	pullUpDnControl(TX20_COMMAND_PIN, PUD_UP);
	
	// Define interruption for edge rising on TXDPIN.
	if (wiringPiISR (TX20_DATA_PIN, INT_EDGE_RISING, &tx20_interrupt ) < 0) {
		fprintf (stderr, "Unable to setup ISR: %s\n", strerror (errno)) ;
		return ;
	}
	
		tx20_last_update = micros();
}

void init_dht22(void) {
	dht22_last_update = micros();
}

static uint8_t sizecvt(const int read) {
	/* digitalRead() and friends from wiringpi are defined as returning a value
	< 256. However, they are returned as int() types. This is a safety function */

	if (read > 255 || read < 0)
	{
		fprintf(stderr, "Invalid data from wiringPi library\n");
		exit(EXIT_FAILURE);
	}
	return (uint8_t)read;
}

/**
 * This is the interruption function called when the GPIO port "TXDPIN" detects a rising edge.
 * When it happens, we check if there is a treatment of this interruption first (bool is_tx20_interrupt).
 * If it's the first interruption, we will check each bit (based on duration of each bit). 
 */
void tx20_interrupt (void) {
	// Local variable initialization
	int i = 0;
	int tx20_dat[6] = {0, 0, 0, 0, 0, 0};

	// this flags let the program to check only the interesting interruption.
	if (!is_tx20_interrupt) {
		// Flag switch.
		is_tx20_interrupt = true;

		// We do a little break to check bit at the half of his duration.
		delayMicroseconds(TX20_BIT_LENGTH / 2);

		// Signal is encoded in 41 bits. Each part of message is endianness. It must be swapped.
		// Each block must be inverted.
		// There is 6 blocks: 
		//	#1: Start Frame 00100
		//	#2: Wind direction (4 bits)
		// 	#3: Wind speed (12 bits)
		//	#4: checksum (4 bits)
		//	#5: Wind direction (4 bits) [not inverted]
		// 	#6: Wind speed (12 bits) [not inverted]
		for (i = 0 ; i < 41 ; i++) {
			if (i < 5) {
				tx20_dat[0] += (1 - digitalRead(TX20_DATA_PIN)) * pow(2, i);
			} else if (i < 9) {
				tx20_dat[1] += (1 - digitalRead(TX20_DATA_PIN)) * pow(2, i - 5);
			} else if (i < 21) {
				tx20_dat[2] += (1 - digitalRead(TX20_DATA_PIN)) * pow(2, i - 9);
			} else if (i < 25) {
				tx20_dat[3] += (1 - digitalRead(TX20_DATA_PIN)) * pow(2, i - 21);
			} else if (i < 29) {
				tx20_dat[4] += (1 - digitalRead(TX20_DATA_PIN)) * pow(2, i - 25);
			} else if (i < 41) {
				tx20_dat[5] += (1 - digitalRead(TX20_DATA_PIN)) * pow(2, i - 29);
			}
			delayMicroseconds(TX20_BIT_LENGTH);
		}

		// checksum verification 
		if (tx20_dat[3] == ((tx20_dat[1] + (tx20_dat[2] >> 8) + ((tx20_dat[2] >> 4) & 0xF) + ((tx20_dat[2]) & 0xF)) & 0xF)) {
			tx20_wind_speed = tx20_dat[2] / 10.0;
			tx20_wind_direction = tx20_dat[1] * 22.5;
			tx20_last_update = micros();
		}
		
		// End of data transmition. The TX20_COMMAND_PIN must be high to stop communication with anemometer.
		digitalWrite(TX20_COMMAND_PIN, HIGH);
	}
}

static int read_dht22_dat(void) {
	uint8_t laststate = HIGH;
	uint8_t counter = 0;
	uint8_t j = 0, i;
	int dht22_dat[5] = {0, 0, 0, 0, 0};

	// pull pin down for 18 milliseconds
	pinMode(DHT22_DATA_PIN, OUTPUT);
	digitalWrite(DHT22_DATA_PIN, HIGH);
	delay(10);
	digitalWrite(DHT22_DATA_PIN, LOW);
	delay(18);
	// then pull it up for 40 microseconds
	digitalWrite(DHT22_DATA_PIN, HIGH);
	delayMicroseconds(40); 
	// prepare to read the pin
	pinMode(DHT22_DATA_PIN, INPUT);

	// detect change and read data
	for ( i = 0 ; i < DHT22_MAXTIMINGS ; i++) {
		counter = 0;
		while (sizecvt(digitalRead(DHT22_DATA_PIN)) == laststate) {
			counter++;
			delayMicroseconds(1);
			if (counter == 255) {
				break;
			}
		}
		laststate = sizecvt(digitalRead(DHT22_DATA_PIN));

		if (counter == 255) break;

		// ignore first 3 transitions
		if ((i >= 4) && (i%2 == 0)) {
			// shove each bit into the storage bytes
			dht22_dat[j / 8] <<= 1;
			if (counter > 16)
				dht22_dat[j / 8] |= 1;
			j++;
		}
	}

	// check we read 40 bits (8bit x 5 ) + verify checksum in the last byte
	// print it out if data is good
	if ((j >= 40) && (dht22_dat[4] == ((dht22_dat[0] + dht22_dat[1] + dht22_dat[2] + dht22_dat[3]) & 0xFF)) ) {
				float t, h;
				
				h = (float)dht22_dat[0] * 256 + (float)dht22_dat[1];
				dht22_humidity = h / 10.0;
				
				t = (float)(dht22_dat[2] & 0x7F)* 256 + (float)dht22_dat[3];
				dht22_temperature = t / 10.0;
				
				if ((dht22_dat[2] & 0x80) != 0) {
					t *= -1;
				}
		
		dht22_last_update = micros();
		return 1;
	} else {
		return 0;
	}
}

static void read_mlx90614(void) {
	unsigned char buf[6];
	unsigned char reg;
	double temp = 0, calc_ir = 0, calc_am = 0;
	
	reg = 7;
	bcm2835_i2c_begin();
	bcm2835_i2c_write(&reg, 1);
	bcm2835_i2c_read_register_rs(&reg, &buf[0], 3);
	temp  = (float) (((buf[1]) << 8) + buf[0]);
	temp  = (temp * 0.02) - 0.01;
	temp  = temp - 273.15;
	calc_ir += temp;
	sleep(1);
	
	reg  = 6;
	bcm2835_i2c_begin();
	bcm2835_i2c_write (&reg, 1);
	bcm2835_i2c_read_register_rs(&reg, &buf[0], 3);
	temp = (float) (((buf[1]) << 8) + buf[0]);
	temp = (temp * 0.02) - 0.01;
	temp = temp - 273.15;
	calc_am += temp;
	sleep(1);
	
	mlx90614_infrared_temperature = calc_ir;
	mlx90614_ambiant_temperature = calc_am;
	
	mlx90614_last_update = micros();
}
