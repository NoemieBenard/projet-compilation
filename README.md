# Pointeurs
Chloé Viennot

## Pour compiler un fichier 

Adapter le nom du fichier ouvert par le script python (simple.c). \
Récupérer l'assembleur affiché par le script dans un fichier test.asm.\
Ceci peut être fait avec la commande suivante:\
`python3.12 simple.c > simple.asm`

Exécuter les commandes :\
    `nasm -f elf64 test.asm` \
    `gcc -no-pie test.o`\
    `./a.out 1 0 0 0`

## Exemples d'utilisation

Il est possible de:

1) déréférencer des variables (autant de fois que l'on veut):\
   `******p`
2) accéder à l'adresse d'une variable:
   `&p`
3) affecter des valeurs via un pointeur:
   `p = &X;`\
   `*p=3`
4) alouer de la mémoire et déréférencer des expressions:\
   `p = malloc(4);`\
   `*(p+1)=3`\
   `X = *(p+3)'

## Exemples de code qui marche

```main(W,X,Y,Z){
    X = &W;
    Y = &X;
    Z = **Y
    return (Z)}
```

```main(W,X,Y,Z){
    W = malloc(8);
    X = W + 10000;
    *X = 6;
    Y = *X
    return (Y)}
```

## Lien vers les diapositives
https://www.canva.com/design/DAGp35LVbNM/bQaTa2yesASrD4jxeXBidg/edit?utm_content=DAGp35LVbNM&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton



