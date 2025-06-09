# Fonction
Abel de Muizon

## Pour compiler un fichier 

Adapter le nom du fichier ouvert par le script python (simple.c). \

Exécuter les commandes :\
    `nasm -f elf64 simple.asm` \
    `gcc -no-pie simple.o`\
    `./a.out arg_1 arg_2 ...`

## Syntaxe 

un if est suivie d'un else. Tout commme un while, la condition de sortie est que l'argument vale 0.

### Définition d'une fonction

`fonction(liste_variable) {
    commande
    return(expression)
} `


Toutes les fonction doivent être définies avant la fonction `main`

### Déclaration d'une variable local dans une fonction

`fonction(x,y) {
    result = x+y
    return(result)
} `
On peut définir des variable local à l'intérieur d'une fonction. L'espace pour celle ci est alloué sur la pile.

### Fonction récurssive

il est possible de faire de la récurssion : 

`fonction(x,y) {
    if(x){
      result = x + fois(x-1,y)
    }else{
      result = 0
    }
    return(result)
} `


### Remarques 

