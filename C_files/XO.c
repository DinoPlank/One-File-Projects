#include<stdio.h>
void setup(char x[3][3]){
    for (int i = 0; i < 3; i++){
        for (int j = 0; j < 3; j++){
            x[i][j]=' ';
        }
    }
}
void printboard(char x[3][3]){
    for (int i = 0; i < 3; i++){
    
        for (int j = 0; j < 3; j++){
            printf(" %c ", x[i][j]);
            if(j==2){printf("\n");}
            else{printf("|");}   
        }
        if(i<2 ){printf("---|---|---\n");}
    }
}
char check(char x[3][3], char y){
    if(x[0][0]==x[1][1] && x[1][1]==x[2][2] && x[1][1]!=' '){return y;}// check diagonal 1
        else if(x[2][0]==x[1][1] && x[1][1]==x[0][2] && x[1][1]!=' '){return y;}// check diagonal 2
    for (int i = 0; i < 3; i++)
    {
        if(x[0][i]==x[1][i] && x[1][i]==x[2][i] && x[1][i]!=' '){return y;}// check columns
            else if (x[i][0]==x[i][1] && x[i][1]==x[i][2] && x[i][1]!=' '){return y;}// check rows
     }
    return 'n';
}
int main(){

char board[3][3]={};
int row=0;
int col=0;
int turn=0;
char winner='n';
char exit='y';
do{
setup(board);
printboard(board);
do{   
    do{
        printf("Player 1(X), enter a column(1-3):");
        scanf("%d", &col);
        printf("Player 1(X), enter a row(1-3):");
        scanf("%d", &row);
        if(board[row-1][col-1]!='O' && board[row-1][col-1]!='X'){
            board[row-1][col-1]='X';turn++; printboard(board); break;}
        else{printf("Spot is already taken\n");}
    }while(1==1);
    winner=check(board, 'X');
    if(turn>8){turn=100; break;}
    do{ if(winner!='n'){break;}
        printf("Player 2(O), enter a column(1-3):");
        scanf("%d", &col);
        printf("Player 2(O), enter a row(1-3):");
        scanf("%d", &row);
        if(board[row-1][col-1]!='X' && board[row-1][col-1]!='O'){
            board[row-1][col-1]='O';turn++; printboard(board); break;}
        else{printf("Spot is already taken\n");}
    }while(1==1);
    if(winner!='n'){break;}
    winner=check(board, 'O');
} while (winner!='X' && winner!='O');
if(turn==100){printf("==================\nGame ended in tie!\n==================");}
if(winner=='X'){printf("================\nThe winner is X!\n================");}
if(winner=='O'){printf("================\nThe winner is O!\n================");}
printf("\nPlay again? (y/n):");
        scanf(" %c", &exit);
}while(exit=='y' || exit=='Y');
    return 0;
}