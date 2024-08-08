# Bài toán đặt ra: 
Tập training có 5 lớp sau:
| Label | Dữ liệu | Ghi chú |
|-|-|-|
| `Library` | R1 = {a<sub>1</sub>, a<sub>2</sub>, ...} | R1 có n<sub>1</sub> phần tử |
| `Student` | R2 = {b<sub>1</sub>, b<sub>2</sub>, ...} | R2 có n<sub>2</sub> phần tử |
| `Type` | R3 = {c<sub>1</sub>, c<sub>2</sub>, ...} | R3 có n<sub>3</sub> phần tử |
| `Authority` | R4 = {d<sub>1</sub>, d<sub>2</sub>, ...} | R4 có n<sub>4</sub> phần tử |
| `Contact` | R5 = {e<sub>1</sub>, e<sub>2</sub>, ...} | R5 có n<sub>5</sub> phần tử |

=> Hãy phân loại văn bản INPUT nhập vào thuộc lớp Label nào trong 5 lớp trên?

# Sử dụng Multinomial Naive Bayes
> p(R1) = p(R2) = p(R3) = p(R4) = p(R5) = <sup>1</sup>&frasl;<sub>5</sub> = p(Ri)

### 1. Xác định từ điển V:
+ Tiêu chí: V gồm tất cả các phần tử không trùng nhau
+ Từ điển: V = {set(R1, R2, R3, R4, R5)} --> z = |V| &le; n<sub>1</sub> + n<sub>2</sub> + n<sub>3</sub> + n<sub>4</sub> + n<sub>5</sub>
---

### 2. Xác định các vector đặc trưng ứng với mỗi lớp theo V:
+ Lập vector số lần xuất hiện từ x<sub>i</sub> của các lớp theo V (dimV = z):
<div style="padding-left: 50px">
    R1 --> x<sub>1</sub> = (a<sub>1z</sub>, a<sub>2z</sub>, ..., a<sub>zz</sub>) <br>
    R2 --> x<sub>2</sub> = (b<sub>1z</sub>, b<sub>2z</sub>, ..., b<sub>zz</sub>) <br>
    R3 --> x<sub>3</sub> = (c<sub>1z</sub>, c<sub>2z</sub>, ..., c<sub>zz</sub>) <br>
    R4 --> x<sub>4</sub> = (d<sub>1z</sub>, d<sub>2z</sub>, ..., d<sub>zz</sub>) <br>
    R5 --> x<sub>5</sub> = (e<sub>1z</sub>, e<sub>2z</sub>, ..., e<sub>zz</sub>) <br> 
    => Với văn bản Test: <br>

        INPUT --> x_inp = (i1, i2, ..., iz)
</div>
    
+ Xét các mẫu R1, R2, R3, R4, R5 lần lượt có N(R1) = n<sub>1</sub>, N(R2) = n<sub>2</sub>, N(R3) = n<sub>3</sub>, N(R4) = n<sub>4</sub>, N(R5) = n<sub>5</sub>
---

### 3. Áp dụng Laplace smoothing với alpha = 1:
+ Sử dụng Laplace Smoothing với alpha = 1, ta có:
<div style="text-align: center;">

    lamdaRi = (element_j + alpha) / (N(Ri) + alpha*z)
</div> 

> với element_j thuộc Ri = {element1, element2, ...}

+ Tính vector cột theo công thức: \
    lamdaR1 = {a<sub>1z</sub>+1/n<sub>1</sub>+z, a<sub>2z</sub>+1/n<sub>1</sub>+z, a<sub>3z</sub>+1/n<sub>1</sub>+z, ..., a<sub>zz</sub>+1/n<sub>1</sub>+z} \
    lamdaR2 = {b<sub>1z</sub>+1/n<sub>2</sub>+z, b<sub>2z</sub>+1/n<sub>2</sub>+z, b<sub>3z</sub>+1/n<sub>2</sub>+z, ..., b<sub>zz</sub>+1/n<sub>2</sub>+z} \
    lamdaR3 = {c<sub>1z</sub>+1/n<sub>3</sub>+z, c<sub>2z</sub>+1/n<sub>3</sub>+z, c<sub>3z</sub>+1/n<sub>3</sub>+z, ..., c<sub>zz</sub>+1/n<sub>3</sub>+z} \
    lamdaR4 = {d<sub>1z</sub>+1/n<sub>4</sub>+z, d<sub>2z</sub>+1/n<sub>4</sub>+z, d<sub>3z</sub>+1/n<sub>4</sub>+z, ..., d<sub>zz</sub>+1/n<sub>4</sub>+z} \
    lamdaR5 = {e<sub>1z</sub>+1/n<sub>5</sub>+z, e<sub>2z</sub>+1/n<sub>5</sub>+z, e<sub>3z</sub>+1/n<sub>5</sub>+z, ..., e<sub>zz</sub>+1/n<sub>5</sub>+z}
---

### 4. Tính xác suất với Multinomial Naive Bayes:
+ Tính xác suất các label tương ứng có trong INPUT:
>   
    p(Ri|x_inp) = p(Ri) * tích(p(x_inp_j|Ri)) = p(Ri) * tích(lamdaRij^x_inp_j)
với i = 1 --> 5, j = 1 --> z

+ Xác suất phân loại văn bản:
> 
    p(Ri|INP) = p(Ri|x_inp) / sum(p(Rj|x_inp)) 

với j = 1 --> 5 
> => Vậy p(R) = max(p(Ri|INP)) --> văn bản thuộc lớp R
