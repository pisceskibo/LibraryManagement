# Thư viện Streamlit
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from chatbotai import classifier


# Hàm đọc file trong bộ dữ liệu
def docfile(path):
    with open(path, 'r', encoding='utf-8') as file:
        data_string = ""
        for line in file:
            data = line.strip()
            data_string += data
    return classifier.format_testcase(data_string)


# Mô hình Multinomial Naive Bayes tự xây dựng 
def multinomial_naivebayes_searching_ai(test_input_array):
    r1 = docfile("chatbotai/dataset/library.txt")
    r2 = docfile("chatbotai/dataset/student.txt")
    r3 = docfile("chatbotai/dataset/type.txt")
    r4 = docfile("chatbotai/dataset/authority.txt")
    r5 = docfile("chatbotai/dataset/contact.txt")

    labels = ["Library", "Student", "Type", "Authority", "Contact"]    
    datasets = [r1, r2, r3, r4, r5]


    ## PHÁT BIỂU BÀI TOÁN
    st.write("## Phát biểu bài toán:")

    # Hiển thị Label
    st.write("**Tập Training:**")
    training_datasets = pd.DataFrame({
            'Danh mục Label': labels,
            'Biến': ['R1', 'R2', 'R3', 'R4', 'R5'],
            'Bộ dữ liệu': [train_data for train_data in datasets],
            'Số phần tử': [len(train_data) for train_data in datasets]
        })
    st.table(training_datasets) # Hiển thị bảng

    # Dữ liệu cần Test
    r_test = []
    for element_identity in test_input_array:
        for rij in datasets:
            if element_identity in rij:
                r_test.append(element_identity)
    if not r_test:
        return "", []
    st.write(f"**Dữ liệu cần Test (formated):** INPUT = {r_test}")
    st.write("**Yêu cầu:** Vậy INPUT thuộc phân loại lớp danh mục nào?")


    ## XÂY DỰNG MÔ HÌNH
    st.write("## Xây dựng mô hình phân loại:")
    N_R1, N_R2, N_R3, N_R4, N_R5 = len(r1), len(r2), len(r3), len(r4), len(r5)
    P_R1 = P_R2 = P_R3 = P_R4 = P_R5 = 1/5
    st.write(f"**Xác suất từng lớp:** P(R1) = P(R2) = P(R3) = P(R4) = P(R5) = {P_R1}")

    # Bộ từ điển V (không chứa dữ liệu bị trùng lặp)
    V = set()
    for element_dataset in datasets:
        V.update(element_dataset)
    vocabulary = list(V)
    z = len(vocabulary)
    st.write(f"**Bộ từ điển** V = {vocabulary} có độ lớn |V| = {z}")

    # Tìm vector tần số xuất hiện theo V
    def get_frequency_vector(ri, vocabulary):
        vector_frequency_ri = [ri.count(v) for v in vocabulary]
        return vector_frequency_ri

    frequency_r1 = get_frequency_vector(r1, vocabulary)
    frequency_r2 = get_frequency_vector(r2, vocabulary)
    frequency_r3 = get_frequency_vector(r3, vocabulary)
    frequency_r4 = get_frequency_vector(r4, vocabulary)
    frequency_r5 = get_frequency_vector(r5, vocabulary)
    frequency_test = get_frequency_vector(r_test, vocabulary)
    st.write("**Lập vector tần số của các lớp theo V:**")
    frequency_table = pd.DataFrame({
            'Vector': ['x1', 'x2', 'x3', 'x4', 'x5', 'x_inp'],
            'Frequency Array': [frequency_r1, frequency_r2, frequency_r3, frequency_r4, frequency_r5, frequency_test]
        })
    st.table(frequency_table) # Hiển thị bảng

    # Áp dụng Laplace Smoothing với alpha = 1
    def get_lamda_Ri(frequency_ri, N_Ri, z, alpha=1):
        return [(element_j + alpha) / (N_Ri + alpha * z) for element_j in frequency_ri]

    lamdaR1 = get_lamda_Ri(frequency_r1, N_R1, z)
    lamdaR2 = get_lamda_Ri(frequency_r2, N_R2, z)
    lamdaR3 = get_lamda_Ri(frequency_r3, N_R3, z)
    lamdaR4 = get_lamda_Ri(frequency_r4, N_R4, z)
    lamdaR5 = get_lamda_Ri(frequency_r5, N_R5, z)
    st.write("**Sử dụng Laplace Smoothing với alpha = 1 để tính toán giá trị Lamda:**")
    laplace_table = pd.DataFrame({
            'Lamda': ['Lamda1', 'Lamda2', 'Lamda3', 'Lamda4', 'Lamda5'],
            'Value of Lamda': [lamdaR1, lamdaR2, lamdaR3, lamdaR4, lamdaR5]
        })
    st.table(laplace_table) # Hiển thị bảng

    # Tính xác suất tương đối
    def get_statistical(P_Ri, lamdaRij, frequency_ij):
        probality = P_Ri
        for j in range(len(lamdaRij)):
            probality *= lamdaRij[j] ** frequency_ij[j]
        return probality

    p_R1_test = get_statistical(P_R1, lamdaR1, frequency_test)
    p_R2_test = get_statistical(P_R2, lamdaR2, frequency_test)
    p_R3_test = get_statistical(P_R3, lamdaR3, frequency_test)
    p_R4_test = get_statistical(P_R4, lamdaR4, frequency_test)
    p_R5_test = get_statistical(P_R5, lamdaR5, frequency_test)

    st.write("**Xác suất tương đối từng lớp:**")
    abs_probabilities = pd.DataFrame({
            'Labels': labels,
            'P(Ri|x_inp)': ['P(R1|x_inp)', 'P(R2|x_inp)', 'P(R3|x_inp)', 'P(R4|x_inp)', 'P(R5|x_inp)'],
            'Xác suất tương đối': [p_R1_test, p_R2_test, p_R3_test, p_R4_test, p_R5_test]
        })
    st.table(abs_probabilities) # Hiển thị bảng

    sum_p_Ri_test = p_R1_test + p_R2_test + p_R3_test + p_R4_test + p_R5_test

    def get_normalization(p_Ri_test, sum_p_Ri_test):
        return p_Ri_test / sum_p_Ri_test

    normalizationR1 = get_normalization(p_R1_test, sum_p_Ri_test)
    normalizationR2 = get_normalization(p_R2_test, sum_p_Ri_test)
    normalizationR3 = get_normalization(p_R3_test, sum_p_Ri_test)
    normalizationR4 = get_normalization(p_R4_test, sum_p_Ri_test)
    normalizationR5 = get_normalization(p_R5_test, sum_p_Ri_test)

    array_normalization_statistical = [normalizationR1, normalizationR2, normalizationR3, normalizationR4, normalizationR5]
    highest_score = max(array_normalization_statistical)
    index_of_max = array_normalization_statistical.index(highest_score)

    return labels[index_of_max], array_normalization_statistical


# Giao diện Streamlit
def main_streamlit():
    st.title("Phân loại danh mục với mô hình Multinomial Naive Bayes")
    st.sidebar.image('static/images/LogoRikkeisoft.png')
    st.sidebar.header("Nhập dữ liệu kiểm tra")
    test_input = st.sidebar.text_input("Nhập dữ liệu cần phân loại:")
    
    if st.sidebar.button("Phân loại") or test_input:
        test_input_array = classifier.format_testcase(test_input)
        
        if not test_input_array:
            st.write("Vui lòng nhập dữ liệu kiểm tra phân loại.")
            return

        result, probabilities = multinomial_naivebayes_searching_ai(test_input_array)

        if not result:
            st.write("Không thể phân loại dữ liệu. Vui lòng kiểm tra lại dữ liệu đầu vào.")
            return
        
        st.write("## Kết quả phân loại mô hình:")
        st.write(f"**Kết quả phân loại:** {result}")
        st.write(f"**Xác suất chính xác từng lớp:**")
        labels = ["Library", "Student", "Type", "Authority", "Contact"]
        
        # Tạo DataFrame cho bảng kẻ
        probabilities_df = pd.DataFrame({
            'Danh mục': labels,
            'Xác suất': [round(prob, 4) for prob in probabilities]
        })
        # Hiển thị bảng
        st.table(probabilities_df)

        fig, ax = plt.subplots()
        ax.bar(labels, probabilities, color='skyblue')
        ax.set_xlabel('Danh mục theo Labels')
        ax.set_ylabel('Xác suất')
        ax.set_title('Xác suất dựa trên mô hình Multinomial Naive Bayes')
        st.pyplot(fig)

if __name__ == "__main__":
    # streamit run streamlitbayes.py
    main_streamlit()
