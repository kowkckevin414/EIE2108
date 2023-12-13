import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import os
import math

def BVQCencode(in_image_filename, out_encoding_result_filename, d):
    
    in_image_filename = mpimg.imread(in_image_filename)
    intensity = np.array(in_image_filename) * 255
    
    # Define general variable
    halved_d = int(d/2) # Length of Subblock
    block_row = int(intensity.shape[0] / d)
    block_column = int(intensity.shape[1] / d)
    byte = int(d * d / 16) 
    if(d == 2): # Bit stuffing
       byte = 1 
    
    # Define the Dictionary Items
    dict_M = np.zeros([block_row, block_column], dtype = 'uint8')
    dict_Sd = np.zeros([block_row, block_column], dtype = 'uint8')
    dict_Idx = np.zeros([block_row * block_column, byte, 4], dtype = 'uint8')
    
    # Create content of each block
    for i in range(0,intensity.shape[0], d): # Column: Intensity
        for j in range(0,intensity.shape[1], d): # Row: Intensity
            # Define general variable
            block = intensity[i:i+d, j:j+d] # Get the block using d as interval
            mean = np.mean(block)
            std = np.std(block) # Standard Deviation
    
            # Define Codebook
            g0 = max(0, mean - std)
            g1 = min(255, mean + std)
            codebook = np.array(([[g0, g0],[g1, g1]], [[g1, g1],[g0, g0]], # c[0], c[1]
                                 [[g0, g1],[g0, g1]], [[g1, g0],[g1, g0]])) # c[2], c[3] 
    
            # Define Subblock (2x2)
            subblock = np.zeros([halved_d,halved_d,2,2])
            for f in range(halved_d): # Column: block
                for g in range(halved_d): # Row: block
                    subblock[f][g] = block[f*2:f*2+2, g*2:g*2+2] 
            
            # Find index by shortest diseance
            bit = 0
            byte_carry= 0
            for a in range(halved_d): # Column: subblock
                for b in range(halved_d): # Row: subblock
                    distance = np.array([]) # Empty the distance array
                    for c in range(4):
                        distance = np.append(distance, np.sum((subblock[a][b] - codebook[c]) ** 2))
                    dict_Idx[int(i/d * block_column + j/d), byte_carry, bit] = np.binary_repr(np.argmin(distance)) # Get the index(Minimum distance) in BINARY
                    bit += 1
                    if(bit == 4): # 4 number(4 x 2bits) to 1 byte --> Carrying system 
                        byte_carry += 1
                        bit = 0
                        
            # Record the Dictionary (Mean & SD)
            dict_M[int(i/d)][int(j/d)] = np.uint8(mean + 0.5)
            dict_Sd[int(i/d)][int(j/d)] = np.uint8(std + 0.5)
    
    # Adjust the Dictionary (Index)
    dict_Idx = dict_Idx.astype(str).tolist() # Covert int to string for concatenating
    for l in range(int(block_column * block_row)): # Every single block
        for o in range(byte): 
            # Covert every binary number to 2 bits
            dict_Idx[l][o] = ['00' if string == '0' else string for string in dict_Idx[l][o]] # Change '0' to '00'
            dict_Idx[l][o] = ['01' if string == '1' else string for string in dict_Idx[l][o]] # Change '1' to '01'
        dict_Idx[l] = [''.join(row) for row in dict_Idx[l]] # Concatenation binary number in array (i.e. [10,11] --> [1011])
        for p in range(len(dict_Idx[l])): 
            dict_Idx[l][p] = int(dict_Idx[l][p],2) # Covert the string to int in DECIMAL
    dict_Idx = np.array(dict_Idx)
    dict_Idx = np.uint8(dict_Idx + 0.5)
    
    # Construct the dictionary
    dict = {"M":dict_M, "Sd":dict_Sd, "Idx":dict_Idx} 
    
    # Consruct the 6 bytes header
    header = np.zeros([6],dtype = 'uint8')
    header[0] = np.uint8(6) # Number of bytes
    header[1] = np.uint8(d) # d
    # header[2] ~ header[3]: amount of block in row
    block_row_hex = np.base_repr(block_row, base = 16) # in HEXADECIMAL (i.e. 255 --> FF) 
    block_row_hex = '0' * (4 - len(block_row_hex)) + block_row_hex  # Insert '0' infront to form 4 bit number (i.e. 00FF)
    header[2] = int(block_row_hex[0] + block_row_hex[1], 16) # 00FF --> 00
    header[3] = int(block_row_hex[2] + block_row_hex[3], 16) # 00FF --> FF
    # header[4] ~ header[5]: amount of block in column
    block_column_hex = np.base_repr(block_column, base = 16) # in HEXADECIMAL (i.e. 255 --> FF) 
    block_column_hex = '0' * (4 - len(block_column_hex)) + block_column_hex # Insert '0' infront to form 4 bit number (i.e. 00FF)
    header[4] = int(block_column_hex[0] + block_column_hex[1], 16) # 00FF --> 00
    header[5] = int(block_column_hex[2] + block_column_hex[3], 16) # 00FF --> FF

    # Record the encoded result in .bvqc file
    file = open(out_encoding_result_filename, "wb")
    for w in header:
        file.write(w)
    for x in range(block_row):
        for y in range(block_column):
            file.write(dict['M'][x][y]) # Mean of block
            file.write(dict['Sd'][x][y]) # SD of block
            for z in range(byte): # Index of block(1/4/16/... bit)
                file.write(dict['Idx'][x * block_column + y][z])
    file.close()

def BVQCdecode(in_encoding_result_filename, out_reconstructed_image_filename):
    
    # Read the general variable
    file = open(in_encoding_result_filename, "rb")
    d = file.read(2)[1] # Size of block
    halved_d = int(d/2)
    byte = int(d * d / 16) 
    if(d == 2): # Bit stuffing
        byte = 1
    # Amount of block in row
    block_row_hex_fh = np.base_repr(file.read(1)[0], base = 16) # Read the first half of row amount in HEXADECIMAL
    block_row_hex_sh = np.base_repr(file.read(1)[0], base = 16) # Read the second half of row amount in HEXADECIMAL
    block_row = int(block_row_hex_fh + block_row_hex_sh, 16) # Combine the first and second half in DECIMAL
    # Amount of block in column
    block_column_hex_fh = np.base_repr(file.read(1)[0], base = 16) # Read the first half of column amount in HEXADECIMAL
    block_column_hex_sh = np.base_repr(file.read(1)[0], base = 16) # Read the second half of column amount in HEXADECIMAL
    block_column = int(block_column_hex_fh + block_column_hex_sh, 16) # Combine the first and second half in DECIMAL
        
    # Define the whole picture
    intensity = np.zeros([d * block_row, d* block_column])
    
    # Decode content of each block
    for i in range(0, d * block_row, d): # Column: Intensity
        for j in range(0, d * block_column, d): # Row: Intensity
            
            # Read the Mean and SD of each block
            mean = file.read(1)[0]
            std = file.read(1)[0]
    
            # Re-generate the codebook
            g0 = max(0, mean - std)
            g1 = min(255, mean + std)
            codebook = np.array(([[g0, g0],[g1, g1]], [[g1, g1],[g0, g0]], 
                                 [[g0, g1],[g0, g1]], [[g1, g0],[g1, g0]]))      
            
            # Reconstruct block by index
            block = np.zeros([halved_d,halved_d,2,2])
            for m in range(byte): # Read 1/4/16/... bit accroding to byte
                Idx = file.read(1)[0]
                Idx = '{0:08b}'.format(Idx) # Read the number in BINARY
                Idx_array = np.zeros([4])
                # Get the binary number from index
                bit = 0 
                for n in range(4): # 8 bit number([0]00/ [1]00/ [2]00/ [3]00)
                    Idx_array[n] = int(Idx[bit:bit+2],2)
                    bit += 2 # [0:2] --> [2:4] --> [4:6] --> [6:8]
                # Reconstruct the subblock by index and codebook
                index_no = 0
                for o in range(halved_d): # Column: subblock
                    for p in range(halved_d): # Row: subblock
                        block[o][p] = codebook[int(Idx_array[index_no])] 
                        index_no += 1
                        if(index_no == 4): # Reset the index number when count to 4
                            index_no = 0
    
            # Save the block into intensity
            for y in range(halved_d): # Column: Block
                for z in range(halved_d): # Row: Block
                    intensity[i+y*2:i+y*2+2, j+z*2:j+z*2+2] = block[y,z]
    file.close()
    
    # Plot the picture and save
    plt.imshow(intensity, cmap = 'gray')
    intensity = intensity / 255
    mpimg.imsave(out_reconstructed_image_filename, intensity, cmap = 'gray')