import copy, numpy as np
np.random.seed(0)

# compute sigmoid nonlinearity
def sigmoid(x):
    output = 1/(1+np.exp(-x))
    return output

# convert output of sigmoid function to its derivative
def sigmoid_output_to_derivative(output):
    return output*(1-output)


# training dataset generation
int2binary = {}    # 
binary_dim = 8

largest_number = pow(2,binary_dim)
binary = np.unpackbits(# 参数的形式：np.unpackbits(np.arrary([[1],[2],[3]]),axis=1)
    np.array([range(largest_number)],dtype=np.uint8).T,axis=1)   
for i in range(largest_number):
    int2binary[i] = binary[i]


# input variables
alpha = 0.1
input_dim = 2
hidden_dim = 16
output_dim = 1


# initialize neural network weights
synapse_0 = 2*np.random.random((input_dim,hidden_dim)) - 1    # [2,16]
synapse_1 = 2*np.random.random((hidden_dim,output_dim)) - 1    # [16,1]
synapse_h = 2*np.random.random((hidden_dim,hidden_dim)) - 1    # [16,16]

synapse_0_update = np.zeros_like(synapse_0)
synapse_1_update = np.zeros_like(synapse_1)
synapse_h_update = np.zeros_like(synapse_h)

# training logic
for j in range(50):
    
    # generate a simple addition problem (a + b = c)
    a_int = np.random.randint(largest_number/2) # int version
    a = int2binary[a_int] # binary encoding

    b_int = np.random.randint(largest_number/2) # int version
    b = int2binary[b_int] # binary encoding

    # true answer
    c_int = a_int + b_int
    c = int2binary[c_int]
    
    # where we'll store our best guess (binary encoded)
    d_print = np.zeros_like(c)

    overallError = 0
    
    layer_2_deltas = list()
    # layer_1_values是16个向量组成的list，每一个向量有16个数值
    layer_1_values = list()
    layer_1_values.append(np.zeros(hidden_dim))
    
    # moving along the positions in the binary encoding
    for position in range(binary_dim):
        
        # generate input and output
        X = np.array([[a[binary_dim - position - 1],b[binary_dim - position - 1]]])
        y = np.array([[c[binary_dim - position - 1]]])
        # y是[[0]] or [[1]]

        # hidden layer (input ~+ prev_hidden)
        # layer_1是16个数值组成的向量。 X是[1,2] synapse_0是[2,16]  后面是 [1,16]×[16,16]
        # 关键语句，隐藏层16个单元的取值由输入×权重 + 上一次隐藏层的16个值×权重
        layer_1 = sigmoid(np.dot(X,synapse_0) + np.dot(layer_1_values[-1],synapse_h))

        # output layer (new binary representation)
        # [1,16]×[16,1]
        layer_2 = sigmoid(np.dot(layer_1,synapse_1))

        # did we miss?... if so, by how much?
        # y 是 0或1，layer_2是sigmoid值
        layer_2_error = y - layer_2
        # 关键语句，根据 f'(x) = f(x)·[1-f(x)] 但是这里乘以error值
        layer_2_deltas.append((layer_2_error)*sigmoid_output_to_derivative(layer_2))
        overallError += np.abs(layer_2_error[0])
    
        # decode estimate so we can print it out
        # layer_2形如[[0.47596279]]，这里四舍五入，得到预测的值
        d_print[binary_dim - position - 1] = np.round(layer_2[0][0])
        
        # store hidden layer so we can use it in the next timestep
        # 保存当前的[1,16]向量
        layer_1_values.append(copy.deepcopy(layer_1))
    
    # [1,16]
    future_layer_1_delta = np.zeros(hidden_dim)
    
    # 开始反向传播
    for position in range(binary_dim):
        
        X = np.array([[a[position],b[position]]])
        # -position-1：-1 -2 -3 ... -8     layer_1--[[16个数]]
        layer_1 = layer_1_values[-position-1]
        prev_layer_1 = layer_1_values[-position-2]
        

        # error at output layer
        layer_2_delta = layer_2_deltas[-position-1]
        # error at hidden layer

        # [1,16]×[16,16] + [[1,1]]×[1,16]点乘[1,16]
        # layer_1_delta [[16个数]]   layer_2_delta   [[0.06822157]]
        layer_1_delta = (future_layer_1_delta.dot(synapse_h.T) + \
            layer_2_delta.dot(synapse_1.T)) * sigmoid_output_to_derivative(layer_1)

        # let's update all our weights so we can try again
        # np.atleast_2d 将输入的元素转换为至少2维
        # np.atleast_2d(layer_1).T--[16,1]  layer_1_delta--[]
        synapse_1_update += np.atleast_2d(layer_1).T.dot(layer_2_delta)    # [16.1]
        synapse_h_update += np.atleast_2d(prev_layer_1).T.dot(layer_1_delta)    # [16,16]
        synapse_0_update += X.T.dot(layer_1_delta)    # []×[1,16]
        
        future_layer_1_delta = layer_1_delta
    

    synapse_0 += synapse_0_update * alpha
    synapse_1 += synapse_1_update * alpha
    synapse_h += synapse_h_update * alpha    

    synapse_0_update *= 0
    synapse_1_update *= 0
    synapse_h_update *= 0
    
    # print out progress
    if(j % 10 == 0):
        print ("Error:" + str(overallError))
        print ("Pred:" + str(d_print))
        print ("True:" + str(c))
        print (a,b)
        out = 0
        for index,x in enumerate(reversed(d_print)):
            out += x*pow(2,index)
        print (str(a_int) + " + " + str(b_int) + " = " + str(out))
        print ("------------")

        