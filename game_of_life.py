import math

# Coordinates to get neighbours.
PIXEL_OFFSETS = [(-1, 1), (0,  1), (1,  1),
                 (-1, 0),          (1,  0),
                 (-1,-1), (0, -1), (1, -1)]

# Offset constants for seeking into bitmap file.
SIZE_OFFSET = 0x12
DEPTH_OFFSET = 0x1c
HEADER_OFFSET = 0x00
IMAGE_OFFSET = 0x36

# Rulestring variations taken from https://conwaylife.com/wiki/List_of_Life-like_rules.
RULESTRINGS = {
    'Default': 'B3/S23',
    'AntiLife': 'B0123478/S01234678',
    'InverseLife': 'B0123478/S34678',
    'Invertamaze': 'B028/S0124',
    'Neon Blobs': 'B08/S4',
    'H-trees': 'B1/S012345678',
    'Fuzz': 'B1/S014567',
    'Gnarl': 'B1/S1',
    'Snakeskin': 'B1/S134567',
    'Solid islands grow amongst static': 'B12678/S15678',
    'Replicator': 'B1357/S1357',
    'Fredkin': 'B1357/S02468',
    'Feux': 'B1358/S0247',
    'Seeds': 'B2/S',
    'Live Free or Die': 'B2/S0',
    'Serviettes': 'B234/S',
    'Iceballs': 'B25678/S5678',
    'Life without death': 'B3/S012345678',
    'DotLife': 'B3/S023',
    'Star Trek': 'B3/S0248',
    'Flock': 'B3/S12',
    'Mazectric': 'B3/S1234',
    'Maze': 'B3/S12345',
    'SnowLife': 'B3/S1237',
    'Corrosion of Conformity': 'B3/S124',
    'EightFlock': 'B3/S128',
    'LowLife': 'B3/S13',
    'EightLife': 'B3/S238',
    'Lifeguard 2': 'B3/S4567',
    'Coral': 'B3/S45678',
    '3-4 Life': 'B34/S34',
    'Dance': 'B34/S35',
    'Bacteria': 'B34/S456',
    'Never happy': 'B345/S0456',
    'Blinkers': 'B345/S2',
    'Assimilation': 'B345/S4567',
    'Long Life': 'B345/S5',
    'Gems': 'B3457/S4568',
    'Gems Minor': 'B34578/S456',
    'B35/S23': 'B35/S23',
    'Land Rush': 'B35/S234578',
    'B35/S236': 'B35/S236',
    'Bugs': 'B3567/S15678',
    'Cheerios': 'B35678/S34567',
    'Holstein': 'B35678/S4678',
    'Diamoeba': 'B35678/S5678',
    'Amoeba': 'B357/S1358',
    'Pseudo Life': 'B357/S238',
    'Geology': 'B3578/S24678',
    'HighFlock': 'B36/S12',
    '2x2': 'B36/S125',
    'IronFlock': 'B36/S128',
    'HighLife': 'B36/S23',
    'Land Rush 2': 'B36/S234578',
    'Blinker Life': 'B36/S235',
    'IronLife': 'B36/S238',
    'Logarithmic': 'B36/S245',
    'Slow Blob': 'B367/S125678',
    'DrighLife': 'B367/S23',
    '2x2 2': 'B3678/S1258',
    'Castles': 'B3678/S135678',
    'Stains': 'B3678/S235678',
    'Day & Night': 'B3678/S34678',
    'LowFlockDeath': 'B368/S128',
    'Life SkyHigh': 'B368/S236',
    'LowDeath': 'B368/S238',
    'Morley': 'B368/S245',
    'DryLife without Death': 'B37/S012345678',
    'DryFlock': 'B37/S12',
    'Mazectric with Mice': 'B37/S1234',
    'Maze with Mice': 'B37/S12345',
    'DryLife': 'B37/S23',
    'Plow World': 'B378/S012345678',
    'Coagulations Stains.': 'B378/S235678',
    'Pedestrian Life without Death': 'B38/S012345678',
    'Pedestrian Flock': 'B38/S12',
    'HoneyFlock': 'B38/S128',
    'Pedestrian Life': 'B38/S23',
    'HoneyLife': 'B38/S238',
    'Electrified Maze': 'B45/S12345',
    'Oscillators Rule': 'B45/S1235',
    'Walled cities': 'B45678/S2345',
    'Majority': 'B45678/S5678',
    'Vote 4/5': 'B4678/S35678',
    'Lifeguard 1': 'B48/S234',
    'Rings \'n\' Slugs': 'B56/S14568',
    'Vote': 'B5678/S45678',
}

INV_RULESTRINGS = {rulestr: name for name, rulestr in RULESTRINGS.items()}

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

def split_rulestring(rulestring: str) -> tuple[str, str]:
    if '/' not in rulestring:
        return '', ''

    B, S = rulestring.split('/')
    return B[1:], S[1:]

class GameOfLife:
    def __init__(self, filename: str, rulestring: str=RULESTRINGS['Default']) -> None:
        # Get birth and survival values from rulestring.
        B_str, S_str = split_rulestring(rulestring)
        self.B = map(int, B_str)
        self.S = map(int, S_str)

        # Get bitmap information from file.
        with open(filename, 'rb') as bmp:
            # Check that we are reading a bmp file.
            if ord(bmp.read(1)) != 0x42 or ord(bmp.read(1)) != 0x4d:
                raise ValueError('not a bitmap file')
            
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
                    self.image.extend(map(invert_byte, bmp.read(self.byte_depth)))

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