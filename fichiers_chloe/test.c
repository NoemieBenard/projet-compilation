main(X,Y,Z){
    X = 1;
    Y = &X;
    *(Y+3)=5;
    Z = *(Y+3)
    return Z
}