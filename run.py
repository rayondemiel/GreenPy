from flask import Flask, render_template

app = Flask("Application")

militants = {
    0: {
        "nom": "Boris",
        "prenom": "Serge",
        "date_naissance": "12/03/1948",
        "organisation": "PCF",
        "biographie": "Syndicaliste CGT (1972-1973), CFDT (1973-1989) puis SUD-PTT (1989-2005) ; cofondateur et membre du conseil scientifique de l’association ATTAC (1998-2021) militant libertaire et écologiste engagé dans la lutte contre les pesticides et le soutien aux victimes."
    },
    1: {
        "nom": "Pomme",
        "prenom": "Louise",
        "date_naissance": "02/06/1985",
        "organisation": "Greenpeace",
        "biographie": "Cheminot et syndicaliste à la CGT puis à SUD-Rail. Militant trostkyste, il adhère au NPA à ces débuts. Il milita activement contre le projet de TGV Lyon-Turin pour ses impacts sociaux et environnementaux."
    }
}

projets_contest = {
    0: {
        "nom": "Projet de centrale nucléaire à Plogoff",
        "date_debut": "1976",
        "date_fin": "1981",
        "description": "En 1975, un accord de principe est pris entre les conseils généraux et le Conseil économique et social pour la construction d'une centrale nucléaire en Bretagne sur 167 hectares de landes bretonnes (4 unités de production de 1 300 MW chacune, soit une puissance totale de 5 200 MW). La prospection en Bretagne retient cinq sites : Beg an Fry en Guimaëc, Ploumoguer, Plogoff (près de la pointe du Raz), Saint-Vio à Tréguennec et Erdeven. En juin 1976, les ingénieurs d'EDF entament les premiers forages de reconnaissance, ce qui provoque les premières réactions importantes des populations jusque là peu informées. La mobilisation à Erdeven et à Ploumoguer sont telles que ces sites sont rapidement écartés. Un comité de défense se crée le 6 juin, à l'initiative du maire de Plogoff, Jean-Marie Kerloch. Le 8 juin, les Plogoffites dressent des barrages à l'entrée de leur commune pendant trois jours, les géologues et techniciens d'EDF devant céder. Le 11 septembre 1978, ce comité décide de créer un GFA (sur le modèle de celui du Larzac) pour rendre plus difficiles les procédures d'expropriations6. Malgré la structuration de ce mouvement antinucléaire7, notamment à travers les CLIN et les CRIN8, l site de Plogoff est retenu le 12 et 25 septembre 1978 par le Conseil économique et social de Bretagne et le conseil général du Finistère. Le 29 novembre 1978, le conseil général du Finistère se prononce pour l'implantation d'une centrale nucléaire à Plogoff par 28 voix contre 17, marquant la fin de la période de la « centrale baladeuse ». Lʼopposition citoyenne ne faiblit pas : début mai 1979, le comité de défense décide d'installer la bergerie alternative de Feunteun-Aod sur le GFA. Le 30 janvier 1980, les dossiers pour l'enquête d'utilité publique sont réceptionnés à la mairie de Plogoff, devant laquelle ils sont brûlés l'après-midi même. Les autorités préfectorales répondent en louant des camionnettes faisant office de « mairies annexes » (protégées par des gendarmes) pour recueillir les avis favorables de la population, si bien que l'enquête d'utilité publique peut débuter le 31 janvier 1980. Pendant l’enquête publique, une radio libre — Radio Plogoff — commence à émettre. Elle diffuse des programmes radiophoniques jusqu’à la victoire des socialistes en 1981. Après l'enquête publique, des manifestations ont lieu, tournant à des affrontements parfois violents avec les CRS. À plusieurs reprises, des manifestants sont interpellés et jugés pour dégradation de bâtiment public et jets de projectiles, la lutte étant désormais perçue comme le combat des « pierres contre des fusils. Le 16 mars 1980, 50 000 personnes manifestent à l'occasion de la clôture de l'enquête d'utilité publique. Le 24 mai 1980, 100 à 150 000 manifestants fêtent la fin de la procédure, 50 à 60 000 restent pour le fest-noz qui clôture la fête.Le 9 avril 1981, lors de son meeting à Brest, le candidat François Mitterrand déclare que Plogoff « ne figure ni ne figurera » dans le plan nucléaire qu'il mettrait en place s'il était élu. Conformément à sa promesse de campagne, le communiqué du 3 juin 1981, publié après le Conseil des ministres du Gouvernement Mauroy du Président Mitterrand, confirme l'abandon des projets d'extension du camp militaire du Larzac et de construction de la centrale nucléaire de Plogoff.\"Lʼopposition citoyenne ne faiblit pas : début mai 1979, le comité de défense décide d'installer la bergerie alternative de Feunteun-Aod sur le GFA. Le 30 janvier 1980, les dossiers pour l enquête d utilité publique sont réceptionnés à la mairie de Plogoff, devant laquelle ils sont brûlés l après-midi même. Les autorités préfectorales répondent en louant des camionnettes faisant office de « mairies annexes » (protégées par des gendarmes) pour recueillir les avis favorables de la population, si bien que l enquête d utilité publique peut débuter le 31 janvier 1980.Lʼopposition citoyenne ne faiblit pas : début mai 1979, le comité de défense décide d installer la bergerie alternative de Feunteun-Aod sur le GFA. Le 30 janvier 1980, les dossiers pour l enquête d utilité publique sont réceptionnés à la mairie de Plogoff, devant laquelle ils sont brûlés l\'après-midi même. Les autorités préfectorales répondent en louant des camionnettes faisant office de « mairies annexes » (protégées par des gendarmes) pour recueillir les avis favorables de la population, si bien que l\'enquête d\'utilité publique peut débuter le 31 janvier 1980."
    },
    1: {
        "nom": "Projet de centrale nucléaire «Superphénix»",
        "date_debut": "1974",
        "date_fin": "1984",
        "description": "Au début de l'année 1977, des débats préparent une « marche pacifique offensive » pendant l'été, à l'initiative en particulier du Comité Malville de Grenoble et de la coordination des comités Malville qui ont leur journal Superpholix et Radio Active, un émetteur clandestin avec des émissions quotidiennes. Avant même que le projet ne démarre, ces actions ont conduit la presse nationale à faire de gros titres sur Superphénix et à présenter les spécificités de la filière à neutrons rapides et caloporteur sodium à l'ensemble des Français. Le 31 juillet 1977, une nouvelle manifestation contre le projet se déroule à Creys-Malville. C'est l'une des plus importantes de l'histoire du mouvement antinucléaire français, avec 20 000 à 40 000 manifestants antinucléaires venus de toute la France et de quelques pays, notamment d'Allemagne. On y déplore la mort d'un manifestant de 31 ans, Vital Michalon (1946-1977), à la suite d'affrontements violents entre manifestants et forces de l'ordre. Il meurt des suites de lésions pulmonaires dues à l'explosion d'une grenade offensive. "
    }
}


@app.route("/")
@app.route("/accueil")
def accueil():
    return render_template("pages/accueil.html", name="accueil", militants=militants, projets_contest=projets_contest)

@app.route("/militant/<int:name_id>")
def militant(name_id):
    return render_template("pages/militant.html", name="militant", militant=militants[name_id])

@app.route("/projet_contest/<int:objContest_id>")
def objContest(objContest_id):
    return render_template("pages/objet_contest.html", name="objet_contest", projet_contest=projets_contest[objContest_id])

if __name__ == "__main__":
    app.run(debug=True)
