main(X,Y,Z){
    Y = malloc(6);
    *(Y+3)=5;
    Z = *(Y+3)
    return (Z)
}