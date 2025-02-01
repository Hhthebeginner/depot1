int tensionDeSortie;

bool messageAffiche = false;
const int buttonPins[] = {2, 3, 4, 5};
const int ledPins[] = {6, 7, 8, 9, 10};



void setup() {

  Serial.begin(9600);

  delay(100); // Attendre un court instant pour stabiliser la lecture

  tensionDeSortie = analogRead(A0);
   Serial.println( tensionDeSortie);
     for (int i = 0; i < 4; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
  }
 
  for (int i = 0; i < 5; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }
 
  Serial.println("Systeme initialise.");
}





void loop() {
  
  if (!messageAffiche) {

    if (tensionDeSortie>=250 && tensionDeSortie <= 252 ) {

      Serial.println("modele 1");
      Serial.println(niveaudesecurite1());
      

    }
    else if (tensionDeSortie>252 && tensionDeSortie <= 408) 
    {

      Serial.println("modele 2");
      Serial.println(niveaudesecurite2());

    } else if (tensionDeSortie>408 && tensionDeSortie <= 492) {

      Serial.println("modele 3");
      Serial.println(niveaudesecurite2());

    } else if (tensionDeSortie>492 && tensionDeSortie <= 576) {

      Serial.println("modele 4");
      Serial.println(niveaudesecurite3());

    } else if (tensionDeSortie>576 &&tensionDeSortie <= 613) {

      Serial.println("modele 5");
      Serial.println(niveaudesecurite3());

    } else if (tensionDeSortie>613 && tensionDeSortie <= 646) {

      Serial.println("modele 6");
      Serial.println(niveaudesecurite4());

    } else if (tensionDeSortie>646 && tensionDeSortie <= 705) {

      Serial.println("modele 7");
      Serial.println(niveaudesecurite4());

    } else if (tensionDeSortie>705 && tensionDeSortie <= 754) {

      Serial.println("modele 8");
      Serial.println(niveaudesecurite5());

    }
     
    else {

      Serial.println("aucune carte ne correspond a(avec accent) cette entree");

    }

    messageAffiche = true; // Empêcher l'affichage multiple
  }





}



bool MA1(){

  int i;

  int correction_reponse[3]={1,0,2};
  Serial.println("pour chacun des choix donner le numéro de la réponse svp");

  Serial.println("question1:DANS QUELLE VILLE AVEZ VOUS fetez vos 16ans?");
  char* reponse1[3]={"0.lisbonne","1.bordeaux","2.toronto"};

  for (i=0;i<3;i++){

    Serial.println(reponse1[i]);

  }

  while(Serial.available()==0){};

  int rp1=Serial.parseInt();

  if (rp1!=correction_reponse[0]){

    Serial.println( "AUTHENTIFICATION 1 echoue");

    return 0;}

  else{

    Serial.println("question2:quelle etait la matiere que vous preferiez a l ecole?");

    char* reponse2[3]={"0.mathematique","1.anglais","2.histoire"};

    for (i=0;i<3;i++){

    Serial.println(reponse2[i]);

  }

  while(Serial.available()==0){};

    int rp2=Serial.parseInt();

  if (rp2!=correction_reponse[1])

  {Serial.println( "AUTHENTIFICATION 1 echoue");

   return 0;}

  else{

  Serial.println("question3:QUELLE EST VOTRE PATISSERIE preferee?");

  char* reponse3[3]={"0.pavlova","1.Tiramissu","2.opera"};

  for (i=0;i<3;i++){

    Serial.println(reponse3[i]);

  }

  while(Serial.available()==0){};

  int rp3=Serial.parseInt();

  if (rp3!=correction_reponse[2])

  {Serial.println( "AUTHENTIFICATION 1 echoue");

  return 0;}

  else{

   Serial.println("authentification reussie.");

   return 1;}



  }

}

}
bool MA2(){
  const int maxAttempts = 4;
const int lockTime = 30000;
 
int correctCombination[] = {1, 2, 3, 4};
int currentStep = 0;
bool isLocked = false;
unsigned long lockStartTime;
 
  if (isLocked) {
    if (millis() - lockStartTime >= lockTime) {
      isLocked = false;
      currentStep = 0;  
      Serial.println("Combinaison bonne.");
    }
    return 1;
  }
 
  int input = readButtons();
  if (input != -1) {
   
    if (input == correctCombination[currentStep]) {
      Serial.print("Bouton ");
      Serial.print(input);
      Serial.println(" correct!");
 
      digitalWrite(ledPins[currentStep], HIGH);  
     
     
      delay(500);
      digitalWrite(ledPins[currentStep], LOW);
 
     
      currentStep++;
     
     
      if (currentStep == 4) {
        Serial.println("Combinaison correcte !");
       
       
        digitalWrite(ledPins[4], HIGH);
       
        delay(2000);
        digitalWrite(ledPins[4], LOW);
        return 1;
       
     
      }
    } else {
      Serial.println("Combinaison incorrecte!");
 
     
      for (int i = 0; i < 3; i++) {
        digitalWrite(ledPins[0], HIGH);
        digitalWrite(ledPins[1], HIGH);
        digitalWrite(ledPins[2], HIGH);
        digitalWrite(ledPins[3], HIGH);
        delay(500);
        digitalWrite(ledPins[0], LOW);
        digitalWrite(ledPins[1], LOW);
        digitalWrite(ledPins[2], LOW);
        digitalWrite(ledPins[3], LOW);
        delay(500);
        return 0;
      }
     
    }
  }
  return 0;
}
 
int readButtons() {
  int input = -1;
  for (int i = 0; i < 4; i++) {
    if (digitalRead(buttonPins[i]) == LOW) {
      input = i + 1;  
      Serial.print("Bouton ");
      Serial.print(i + 1);
      Serial.println(" presse.");
      break;  
    }
  }
  return input;  
}
 

 bool MA3(){

 String couleuryeux="bleus";

 Serial.println("Quelle est la couleur de vos yeux?");

 while(Serial.available()==0){};

 String reponse=Serial.readString();

 if(reponse==couleuryeux){

  return 1;

  }

  else{

    return 0;

  }

 }

 bool MA5(){

   int i;

  String nomSaisi;

  String idSaisi;

  String nom[16]={"A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P"};

  String id[16]={"A000","A100","A200","A300","A500","A600","A700","A800","A900","B100","B200","B300","B400","B400","B500","B600"};

  Serial.println("veuillez saisir votre l'initial de votre nom");

  while(Serial.available()==0){};

  nomSaisi=Serial.readString();

  Serial.println("veuillez saisir votre id ");

  int indiceNom;

  bool validenom=false;

  for (i=0;i<16;i++){

   if (nom[i]==nomSaisi){

    indiceNom=i;

    validenom=true;}

  }

  if(!validenom){

    return 0;}

    else{

      if(id[indiceNom]==idSaisi){

    return true;

      }

  }

  }

 bool MA4(){

 String main="droite";

 Serial.println("Quelle est la main que vous poser?");

 while(Serial.available()==0){}

 String reponsedigital=Serial.readString();

 if(reponsedigital==main){

  return 1;

  }

  else{

    return 0;

  }

 }
 String niveaudesecurite1(){
  if( MA1()&& MA3()){
    String a="authentification reussie ";
    return a;
  }
  else{
    String a="authentification echoue";
    return a;
  }
 }

String niveaudesecurite2(){
  if( MA1()&& MA4()){
    String a="authentification reussie ";
    return a;
  }
  else{
    String a="authentification echoue";
    return a;
    
  }
 }

String niveaudesecurite3(){
  if( MA2()&& MA4()){
    String a="authentification reussie,/n ouverture du coffre";
    return a;
  }
  else{
    String a="authentification echoue";
    return a;
  }
 }

String niveaudesecurite4(){
  if( MA1()&& MA2()&&MA3()&&MA4()){
    String a="authentification reussie ";
    return a;
  }
  else{
    String a="authentification echoue";
    return a;
  }
 }
String niveaudesecurite5(){
  if( MA1()&& MA2()&& MA3()&& MA4()&&MA5()){
    String a="authentification reussie ";
    return a;
  }
  else{
    String a="authentification echoue";
    return a;
  }
 }


   









