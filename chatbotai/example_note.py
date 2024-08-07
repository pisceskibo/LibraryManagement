"""
Bài toán: Tập training có 5 lớp sau:
+ "Library"     R1 = {"Sách", "Book", "Document", "Truyện"}                 --> R1 có 4 phần tử
+ "Student"     R2 = {"Employee", "Teacher", "Student"}                     --> R2 có 3 phần tử
+ "Type"        R3 = {"Loại", "Type"}                                       --> R3 có 2 phần tử
+ "Authority"   R3 = {"Author", "Information"}                              --> R4 có 2 phần tử
+ "Contact"     R5 = {"Phone", "Email", "Rate"}                             --> R5 có 3 phần tử

=> Hãy phân loại INPUT thuộc lớp Label trong 5 lớp trên 
INPUT = {"Document", "Book", "for", "Teacher"}
--> Tối giản: INPUT = {"Document", "Book", "Teacher"} --> 3, 2, 6
"""

# Sử dụng Multinomial Naive Bayes
"""
p(R1) = p(R2) = p(R3) = p(R4) = p(R5) = 1/5 = p(Ri)
+ Từ điển: V = {"Sách", "Book", "Document", "Truyện",
                "Employee", "Teacher", "Student", "Loại", "Type",
                "Author", "Information",
                "Phone", "Email", "Rate"}
    --> z = |V| = 14
+ Lập vector số lần xuất hiện từ x_i của các lớp theo V:
    R1 --> x1 = (1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    R2 --> x2 = (0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0)
    R3 --> x3 = (0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0)
    R4 --> x4 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0)
    R5 --> x5 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1)
    Với văn bản Test:
        INPUT --> x_inp = (0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0) --> 2, 3, 6

+ Xét R1, R2, R3, R4, R5 có N(R1) = 4, N(R2) = 3, N(R3) = 2, N(R4) = 2, N(R5) = 3
+ Sử dụng Laplace Smoothing với alpha = 1
    lamdaRi = (element_j + alpha) / (N(Ri) + alpha*z)
    với element_j nằm trong Ri = {element1, element2, ...}

+ Tính vector cột theo công thức: 
    lamdaR1 = {1+1/4+14, 1+1/4+14, 1+1/4+14, 1+1/4+14, 
                0+1/4+14, 0+1/4+14, 0+1/4+14, 0+1/4+14, 0+1/4+14, 0+1/4+14, 0+1/4+14, 0+1/4+14, 0+1/4+14, 0+1/4+14}
             = {2/18, 2/18, 2/18, 2/18, 1/18, 1/18, 1/18, 1/18, 1/18, 1/18, 1/18, 1/18, 1/18, 1/18}
    lamdaR2 = {0+1/3+14, 0+1/3+14, 0+1/3+14, 0+1/3+14, 1+1/3+14, 1+1/3+14, 1+1/3+14,
                0+1/3+14, 0+1/3+14, 0+1/3+14, 0+1/3+14, 0+1/3+14, 0+1/3+14, 0+1/3+14}
             = {1/17, 1/17, 1/17, 1/17, 2/17, 2/17, 2/17, 1/17, 1/17, 1/17, 1/17, 1/17, 1/17, 1/17}
    lamdaR3 = {1/16, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16, 2/16, 2/16, 1/16, 1/16, 1/16, 1/16, 1/16}
    lamdaR4 = {1/16, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16, 1/16, 2/16, 2/16, 1/16, 1/16, 1/16}
    lamdaR5 = {1/18, 1/18, 1/18, 1/18, 1/18, 1/18, 1/18, 1/18, 1/18, 1/18, 1/18, 2/18, 2/18, 2/18}

+ Tính xác suất các label có trong INPUT: (đại lượng đồng biến với xác suất)
    p(Ri|x_inp) = p(Ri) * tích(p(x_inp_j|Ri)) = p(Ri) * tích(lamdaRij^x_inp_j)
    với i = 1 --> 5
        j = 1 --> 14

    p(R1|x_inp) = p(R1) * tích(lamdaR1j^x_inp_j) 
                = 1/5 * (2/18)^1 * (2/18)^1 * (1/18)^1 = 1/7290 = 1.37*10^-4
    p(R2|x_inp) = p(R2) * tích(lamdaR2j^x_inp_j)
                = 1/5 * (1/17)^1 * (1/17)^1 * (2/17)^1 = 2/24565 = 8.14*10^-5
    p(R3|x_inp) = p(R3) * tích(lamdaR3j^x_inp_j)
                = 1/5 * (1/16)^1 * (1/16)^1 * (1/16)^1 = 1/20480 = 4.88*10^-5
    p(R4|x_inp) = p(R4) * tích(lamdaR4j^x_inp_j)
                = 1/5 * (1/16)^1 * (1/16)^1 * (1/16)^1 = 1/20480 = 4.88*10^-5
    p(R5|x_inp) = p(R5) * tích(lamdaR5j^x_inp_j)
                = 1/5 * (1/18)^1 * (1/18)^1 * (1/18)^1 = 1/29160 = 3.43*10^-5

+ Xác suất phân loại văn bản: (tính xác suất chuẩn hóa)
    p(Ri|INP) = p(Ri|x_inp) / sum(p(Rj|x_inp)) với j = 1 --> 5

    p(R1|INP) = p(R1|x_inp) / sum(p(Rj|x_inp)) = 0.391
    p(R2|INP) = p(R2|x_inp) / sum(p(Rj|x_inp)) = 0.232
    p(R3|INP) = p(R3|x_inp) / sum(p(Ri|x_inp)) = 0.139
    p(R4|INP) = p(R4|x_inp) / sum(p(Ri|x_inp)) = 0.139
    p(R5|INP) = p(R5|x_inp) / sum(p(Ri|x_inp)) = 0.097

=> Văn bản thuộc lớp R1 tức "Library"
"""
