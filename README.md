# Structs
Noémie Bénard

## Pour compiler un fichier 

Adapter le nom du fichier ouvert par le script python (simple.c). \
Récupérer l'assembleur affiché par le script dans un fichier test.asm.

Exécuter les commandes :\
    `nasm -f elf64 test.asm` \
    `gcc -no-pie test.o`\
    `./a.out argc argv`

## Syntaxe 

### Définition d'une struct

`typedef struct {
    int x;
    int y;
} Point;`

`typedef struct { 
    Point p1;
    Point p2;
} Ligne;`

Toutes les structures doivent être définies avant la fonction `main`

### Déclaration d'un objet de type struct

`Point p;`\
On peut définir des objets de type struct à l'intérieur de main. Par défaut l'espace pour p est alloué sur la pile et ses attributs ne sont pas initialisés.

### Accès à un attribut

Affectation : `p.x = 2;` 

Valeur de retour :  l'attribut peut être le résultat de main
```
main(){
    Point p;
    p.x = 2
    return(p.x)
}
```

Possibilité d'imbriquer les structures : le code suivant est syntaxiquement correct
```
typedef struct {
    int x;
    int y;
} Point;

typedef struct {
    Point p1;
    Point p2;
} Ligne;

typedef struct {
    Ligne l;
} Test;

main(x,y){
    Point p;
    Ligne l;
    p.x = 5;
    l.p1.x = 2;
    Test t;
    t.l.p1.y = 1
    return (t.l.p1.y)
}
```

### Opérations sur les attributs 
Les opérations suivantes sur les attributs fonctionnent :\
`p.x = p.x + 2;` (si p.x a été initialisé auparavant)

```
Ligne l;
l.p1.x = p.x + 2;
```


### Remarques 


