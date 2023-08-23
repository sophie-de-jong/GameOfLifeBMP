import math
import re

# Coordinates to get neighbours.
PIXEL_OFFSETS = [(-1, 1), (0,  1), (1,  1),
                 (-1, 0),          (1,  0),
                 (-1,-1), (0, -1), (1, -1)]

# Offset constants for seeking into bitmap file.
SIZE_OFFSET = 0x12
DEPTH_OFFSET = 0x1c
HEADER_OFFSET = 0x00
IMAGE_OFFSET = 0x36

# Regular expression for parsing rulestrings.
RULESTR_FORMAT = re.compile(r"""
    \A\s*                   # Optional whitespace at the beginning.
    B                       # B character indicating birth values.
    (?P<birth>\d*)          # Capture group for all birth values.
    /S                      # / and S indicating survival values.
    (?P<survival>\d*)       # Capture group for all surivial values.
    \s*\Z                   # Optional whitespace to finish.
""", re.VERBOSE)

# Concatenates bytes at the binary level.
# e.g. concat_bits([0b11, 0b010]) -> 0b11010
# Used to combine the rgb bytes of a pixel into one large integer.
def concat_bits(byte_array, shift_by: int=8) -> int:
    # Results in little endian (most significant byte first) which is standard on intel chips.
    result = 0
    for n in byte_array:
        # Append the new bits by shifting the previous bits.
        result = (result << shift_by) | n
    return result

# Invert a byte so that 0b0000 becomes 0b1111.
# Used when reading in a file so that a pixel of 0 represents
# a white pixel.
def invert_byte(byte: int) -> int:
    # Must be masked with 255 to cancel out any inverted sign bits.
    return ~byte & 0xff

class GameOfLife:
    def __init__(self, filename: str, rulestring: str='B3/S23', is_reversed: bool=True) -> None:
        # Get birth and survival values from rulestring.
        rules = RULESTR_FORMAT.match(rulestring)
        self.birth_values = [int(n) for n in rules['birth']]
        self.survival_values = [int(n) for n in rules['survival']]

        # Get bitmap information from file.
        with open(filename, 'rb') as bmp:
            # Check that we are reading a bmp file.
            if ord(bmp.read(1)) != 0x42 or ord(bmp.read(1)) != 0x4d:
                raise ValueError('not a bitmap file')
            
            # Flag indicating whether to reverse any black and white pixels.
            # On: alive bit is 1
            # Off: alive bit is 0
            self.is_reversed = is_reversed
            
            # Get width and height.
            bmp.seek(SIZE_OFFSET)
            self.width = int.from_bytes(bmp.read(4), byteorder='little')
            self.height = int.from_bytes(bmp.read(4), byteorder='little')

            # Get bits per pixel and bytes per pixel.
            bmp.seek(DEPTH_OFFSET)
            self.bit_depth = int.from_bytes(bmp.read(2), byteorder='little')
            self.byte_depth = self.bit_depth // 8

            # Check that bit depth is valid.
            if self.bit_depth % 8 != 0:
                raise ValueError(f'unsupported bit depth for {filename}')

            # Calculate row size for padding.
            self.row_size = math.ceil(self.bit_depth * self.width / 32) * 4

            # Get all header bytes.
            bmp.seek(HEADER_OFFSET)
            self.header = bmp.read(IMAGE_OFFSET)

            # Get image bytes as integers.
            # Flip all the bits such that a black pixel corresponds to logical ones.
            self.image = []
            for y in range(self.height):
                # Seek to start of new row.
                bmp.seek(self.row_size * y + IMAGE_OFFSET)

                # Read a row of bytes and extend image list.
                for x in range(self.width):
                    if self.is_reversed:
                        # Map the invert_byte() function to each byte that's read.
                        self.image.extend(map(invert_byte, bmp.read(self.byte_depth)))
                    else:
                        self.image.extend(bmp.read(self.byte_depth))

    # Read one row of pixels given a y-level.
    # Used when padding the row to a multiple of 4 when writing back to a file.
    def get_row(self, y: int) -> int:
        # y-level can't be negative or greater than the height of the image.
        if y < 0 or y >= self.height:
            raise ValueError(f'y must be between 0 and {self.height}')
        
        # Compute starting index.
        i = y * self.width * self.byte_depth

        # Iterate through the row and append to list.
        return [self.image[i + j] for j in range(self.width * self.byte_depth)]
    
    # Read one pixel given x, y coordinates.
    # Used for performing the game of life algorithm.
    def get_pixel(self, x: int, y: int) -> int:
        # Ensure that the coordinates lie within the bounds of the bitmap.
        if x < 0 or x >= self.width or y < 0 or y >= self.width:
            return 0

        # Flatten 2D coordinates to 1D index.
        i = (x + y * self.width) * self.byte_depth

        # Ensure that i is a valid index for self.image.
        if i >= len(self.image):
            return 0

        # Concatenate the bytes together to form one big integer.
        return concat_bits(self.image[i + j] for j in range(self.byte_depth))

    def tick(self) -> None:
        # Run one iteration of the Game of Life.
        # Takes approximately one second to run with recommended file size.

        # Compute mask for checking one layer of neighbours.
        NEIGHBOUR_Z_MASK = concat_bits([1] * 8, shift_by=self.bit_depth)

        # Initialize new list to hold image bytes.
        new_image = []

        # Loop through entire file as a 2D image.
        for y in range(self.height):
            for x in range(self.width):
                # Get image pixel and neighbours at coordinate.
                pixel = self.get_pixel(x, y)

                # Concatenate all neighbouring pixels into one integer.
                cells = (self.get_pixel(x + offset[0], y + offset[1]) for offset in PIXEL_OFFSETS)
                neighbours = concat_bits(cells, shift_by=self.bit_depth)

                # Copy the mask from the constant as to not mutate the original variable.
                mask = NEIGHBOUR_Z_MASK

                # Iterate through bit depth and play the Game of Life.
                for z in range(self.bit_depth):
                    # Get number of alive neighbours.
                    alive = (neighbours & mask).bit_count()

                    # Get bit using the mask.
                    bit = pixel & mask

                    # Test if bit is alive and must be killed.
                    if bit and alive not in self.survival_values:
                        # Kill bit at index.
                        pixel &= ~mask

                    # Test if bit is dead and must be reborn.
                    if not bit and alive in self.birth_values:
                        # Rebirth bit at index.
                        pixel |= mask & (1 << self.bit_depth) - 1

                    # Shift the mask by 1 to indicate next file depth.
                    mask <<= 1

                # Append each colour from the pixel back to the list.
                for i in range(self.bit_depth - 8, -1, -8):
                    new_image.append((pixel >> i) & 0xff)

        # Update current image.
        self.image = tuple(new_image)

    # Save the current generation to a new file.
    def save_as(self, filename: str) -> None:  
        # Save the current BMP under a file name.
        with open(filename, 'wb') as bmp:
            bmp.write(self.header)
            for y in range(self.height):
                row = self.get_row(y)

                # Invert each bit again if black/white reverse flag is True.
                if self.is_reversed:
                    # Flip all the bits back into its original state so that all 
                    # logical ones become white pixels.
                    bmp.write(bytes(map(invert_byte, row)))
                else:
                    bmp.write(bytes(row))

                # Account for padding.
                bmp.write(bytes([0] * (self.row_size - len(row))))

if __name__ == '__main__':
    bmp = GameOfLife('Conways_game_of_life_breeder_animation.bmp')
    bmp.tick()
    bmp.save_as('test.bmp')