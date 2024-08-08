import re 

# Xử lý dữ liệu cần test
def format_testcase(test_input):
    # Chuyển thành chữ thường
    test_input = test_input.lower()
    
    # Xóa các ký tự đặc biệt và thay thế bằng khoảng trắng, ngoại trừ các ký tự có dấu
    test_input = re.sub(r'[^\w\s]', ' ', test_input)
    
    # Xóa khoảng trắng dư thừa
    test_input = re.sub(r'\s+', ' ', test_input).strip()

    # Chuyển thành mảng các từ
    words_array = test_input.split()
    
    return words_array


# Xây dựng chức năng phân loại danh mục tự động
def naivebayes_searching_ai(test_input_array):
    # Đọc file lấy dữ liệu tập training
    def docfile(path):
        file = open(path, 'r', encoding='utf-8')        # Mở file
        data_string = ""
        for line in file:
            data = line.strip()
            data_string += data

        data_string = data_string.strip()
        file.close()
        return format_testcase(data_string)
        
    r1 = docfile("chatbotai/dataset/library.txt")
    r2 = docfile("chatbotai/dataset/student.txt")
    r3 = docfile("chatbotai/dataset/type.txt")
    r4 = docfile("chatbotai/dataset/authority.txt")
    r5 = docfile("chatbotai/dataset/contact.txt")

    # Bộ dữ liệu tập training
    labels = ["Library", "Student", "Type", "Authority", "Contact"]    
    datasets = [r1, r2, r3, r4, r5]  

    # Bộ dữ liệu test
    r_test = []
    for element_identity in test_input_array:
        for rij in datasets:
            if element_identity in rij:
                r_test.append(element_identity)
    if r_test == []:
        return ""

    # Số lượng mẫu tương ứng
    N_R1 = len(r1)
    N_R2 = len(r2)
    N_R3 = len(r3)
    N_R4 = len(r4)
    N_R5 = len(r5)

    # Xác suất từng lớp
    P_R1 = P_R2 = P_R3 = P_R4 = P_R5 = 1/5


    # Tạo từ điển V
    V = set()
    for element_dataset in datasets:
        V.update(element_dataset)
    vocabulary = list(V)
    z = len(vocabulary)         # |V| = z


    # Lập vector tần số xuất hiện của từ x_i theo V
    def get_frequency_vector(ri, vocabulary):
        vector_frequency_ri = []
        for v in vocabulary:
            count = 0
            for element in ri:
                if element == v:
                    count += 1
            vector_frequency_ri.append(count)
        return vector_frequency_ri

    frequency_r1 = get_frequency_vector(r1, vocabulary)
    frequency_r2 = get_frequency_vector(r2, vocabulary)
    frequency_r3 = get_frequency_vector(r3, vocabulary)
    frequency_r4 = get_frequency_vector(r4, vocabulary)
    frequency_r5 = get_frequency_vector(r5, vocabulary)
    # Tần số cho dữ liệu test
    frequency_test = get_frequency_vector(r_test, vocabulary)


    # Sử dụng Laplace Smoothing với alpha = 1
    def get_lamda_Ri(frequency_ri,  N_Ri, z, alpha = 1):
        vector_lamda = []
        for element_j in frequency_ri:
            lamda_j = (element_j + alpha) / (N_Ri + alpha*z)
            vector_lamda.append(lamda_j)
        return vector_lamda

    lamdaR1 = get_lamda_Ri(frequency_r1, N_R1, z)
    lamdaR2 = get_lamda_Ri(frequency_r2, N_R2, z)
    lamdaR3 = get_lamda_Ri(frequency_r3, N_R3, z)
    lamdaR4 = get_lamda_Ri(frequency_r4, N_R4, z)
    lamdaR5 = get_lamda_Ri(frequency_r5, N_R5, z)


    # Tính xác suất chưa chuẩn hóa
    def get_statistical(P_Ri, lamdaRij, frequency_ij):
        probality = P_Ri
        for j in range(len(lamdaRij)):
            probality = probality * lamdaRij[j]**frequency_ij[j]
        return probality

    p_R1_test = get_statistical(P_R1, lamdaR1, frequency_test)
    p_R2_test = get_statistical(P_R2, lamdaR2, frequency_test)
    p_R3_test = get_statistical(P_R3, lamdaR3, frequency_test)
    p_R4_test = get_statistical(P_R4, lamdaR4, frequency_test)
    p_R5_test = get_statistical(P_R5, lamdaR5, frequency_test)
    sum_p_Ri_test = p_R1_test + p_R2_test + p_R3_test + p_R4_test + p_R5_test


    # Tính xác suất đã chuẩn hóa
    def get_normalization(p_Ri_test, sum_p_Ri_test):
        return p_Ri_test / sum_p_Ri_test

    normalizationR1 = get_normalization(p_R1_test, sum_p_Ri_test)
    normalizationR2 = get_normalization(p_R2_test, sum_p_Ri_test)
    normalizationR3 = get_normalization(p_R3_test, sum_p_Ri_test)
    normalizationR4 = get_normalization(p_R4_test, sum_p_Ri_test)
    normalizationR5 = get_normalization(p_R5_test, sum_p_Ri_test)

    array_normalization_statistical = [normalizationR1, normalizationR2, normalizationR3, normalizationR4, normalizationR5]
    highest_score = max(array_normalization_statistical)

    # Tìm chỉ số có xác suất cao nhất
    index_of_max = array_normalization_statistical.index(highest_score)
    return labels[index_of_max]
