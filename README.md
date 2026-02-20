# ProjectiveAR_Per_Usz

## Adaptation du dispositif matériel (Écran PC + Webcam)
En l'absence d'un vidéoprojecteur physique pour réaliser les tests, le système a été adapté pour utiliser un écran d'ordinateur, qui fait simultanément office de "plateau physique" et de "projecteur". Cette configuration simule parfaitement le pipeline de Réalité Augmentée Projective attendu, mais a nécessité les ajustements suivants dans le code :

Calibration de la caméra et Zone de Silence (Quiet Zone) : Lors de l'étape de calibration de la caméra, la méthode drawBlack() du projecteur a été modifiée pour générer et afficher les 4 marqueurs ArUco directement à l'écran. Pour permettre leur détection, un fond blanc (cst.WHITE) et des marges ont été ajoutés afin de respecter la "zone de silence" indispensable à l'algorithme ArUco.

Pour la détéction de mouvement, nous avons utilisé une gomette que nous collions sur l'écran de l'ordinateur.

Vidéo de démonstration : 



https://github.com/user-attachments/assets/3e07aa57-8132-4552-9c1c-137f21615437


