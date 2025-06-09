main(W,X,Y,Z){
    X = &W;
    Y = &X;
    Z = **Y
    return (Z)
}