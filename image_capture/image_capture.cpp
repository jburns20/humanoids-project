//
// begin license header
//
// This file is part of Pixy CMUcam5 or "Pixy" for short
//
// All Pixy source code is provided under the terms of the
// GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
// Those wishing to use Pixy source code, software and/or
// technologies under different licensing terms should contact us at
// cmucam@cs.cmu.edu. Such licensing terms are available for
// all portions of the Pixy codebase presented here.
//
// end license header
//

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>

#include <QTGui/QImage.h>
#include "pixy.h"

#define BLOCK_BUFFER_SIZE    25

#define RGB(r,g,b) ((((r) & 0xF8) << 8) | (((g) & 0xFC) << 3) | (((b) & 0xF8) >> 3))
#define RED RGB(255,0,0)
#define GREEN RGB(0,255,0)
#define BLUE RGB(0,0,255)
#define WHITE RGB(255,255,255)
#define BLACK RGB(0,0,0)
#define HEX(h) (RGB(((h)>>16),((h)>>8),(h)))

// Pixy Block buffer // 
struct Block blocks[BLOCK_BUFFER_SIZE];

static bool run_flag = true;

void handle_SIGINT(int unused)
{
  // On CTRL+C - abort! //

  run_flag = false;
}

inline void interpolateBayer(unsigned int width, unsigned int x, unsigned int y, unsigned char *pixel, unsigned int &r, unsigned int &g, unsigned int &b)
{
    if (y&1)
    {
        if (x&1)
        {
            r = *pixel;
            g = (*(pixel-1)+*(pixel+1)+*(pixel+width)+*(pixel-width))>>2;
            b = (*(pixel-width-1)+*(pixel-width+1)+*(pixel+width-1)+*(pixel+width+1))>>2;
        }
        else
        {
            r = (*(pixel-1)+*(pixel+1))>>1;
            g = *pixel;
            b = (*(pixel-width)+*(pixel+width))>>1;
        }
    }
    else
    {
        if (x&1)
        {
            r = (*(pixel-width)+*(pixel+width))>>1;
            g = *pixel;
            b = (*(pixel-1)+*(pixel+1))>>1;
        }
        else
        {
            r = (*(pixel-width-1)+*(pixel-width+1)+*(pixel+width-1)+*(pixel+width+1))>>2;
            g = (*(pixel-1)+*(pixel+1)+*(pixel+width)+*(pixel-width))>>2;
            b = *pixel;
        }
    }
}

int renderBA81(uint8_t renderFlags, uint16_t width, uint16_t height, uint32_t frameLen, uint8_t *frame)
{
    uint16_t x, y;
    uint32_t *line;
    uint32_t r, g, b;

    // skip first line
    frame += width;

    // don't render top and bottom rows, and left and rightmost columns because of color
    // interpolation
    QImage img(width-2, height-2, QImage::Format_RGB32);

    for (y=1; y<height-1; y++)
    {
        line = (unsigned int *)img.scanLine(y-1);
        frame++;
        for (x=1; x<width-1; x++, frame++)
        {
            interpolateBayer(width, x, y, frame, r, g, b);
            *line++ = (0xff<<24) | (r<<16) | (g<<8) | (b<<0);
        }
        frame++;
    }
    // send image to ourselves across threads
    // from chirp thread to gui thread
    //emit image(img, renderFlags);
    img.save("output.jpg");

    //m_background = img;

    return 0;
}

int main(int argc, char * argv[])
{
  int      i = 0;
  int      index;
  int      blocks_copied;
  int      pixy_init_status;
  char     buf[128];

  // Catch CTRL+C (SIGINT) signals //
  signal(SIGINT, handle_SIGINT);

  printf("Hello Pixy:\n libpixyusb Version: %s\n", __LIBPIXY_VERSION__);

  // Connect to Pixy //
  pixy_init_status = pixy_init();

  // Was there an error initializing pixy? //
  if(pixy_init_status != 0)
  {
    // Error initializing Pixy //
    printf("pixy_init(): ");
    pixy_error(pixy_init_status);

    return pixy_init_status;
  }

  // Request Pixy firmware version //
  {
    uint16_t major;
    uint16_t minor;
    uint16_t build;
    int      return_value;

    return_value = pixy_get_firmware_version(&major, &minor, &build);

    if (return_value) {
      // Error //
      printf("Failed to retrieve Pixy firmware version. ");
      pixy_error(return_value);

      return return_value;
    } else {
      // Success //
      printf(" Pixy Firmware Version: %d.%d.%d\n", major, minor, build);
    }
  }
  
  int32_t response;
  
  int retval = pixy_command("runprogArg",
                                UINT8(8),
                                INT32(1),
                                END_OUT_ARGS,
                                &response,
                                END_IN_ARGS);
                                
  printf("runprogArg retval: %d, response: %d\n", retval, response);
  
  uint32_t fourcc;
  int8_t renderflags;
  uint16_t width, height;
  uint32_t numPixels;
  uint8_t * pixels;
  
  retval = pixy_command("cam_getFrame",  // String id for remote procedure
                                 UINT8(0x21),     // mode
                                 UINT16(0),        // xoffset
                                 UINT16(0),         // yoffset
                                 UINT16(320),       // width
                                 UINT16(200),       // height
                                 END_OUT_ARGS,      // separator
                                 &response, // pointer to the memory address for return value
                                 &fourcc,
                                 &renderflags,
                                 &width,
                                 &height,
                                 &numPixels,
                                 &pixels,           // pointer to mem address for returned frame
                                 END_IN_ARGS);
  
  printf("getFrame retval: %d, response: %d\n", retval, response);

  FILE* x = fopen("output.RAW", "w");
  fwrite(pixels, 1, numPixels, x);
  fclose(x);
  
  renderBA81(renderflags, width, height, numPixels, pixels);
  
  
  //printf("Detecting blocks...\n");
  /*while(run_flag)
  {
    // Wait for new blocks to be available //
    while(!pixy_blocks_are_new() && run_flag); 

    // Get blocks from Pixy //
    blocks_copied = pixy_get_blocks(BLOCK_BUFFER_SIZE, &blocks[0]);

    if(blocks_copied < 0) {
      // Error: pixy_get_blocks //
      printf("pixy_get_blocks(): ");
      pixy_error(blocks_copied);
    }

    // Display received blocks //
    printf("frame %d:\n", i);
    for(index = 0; index != blocks_copied; ++index) {    
       blocks[index].print(buf);
       printf("  %s\n", buf);
    }
    i++;
  }*/
  pixy_close();
}
