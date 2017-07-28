=============================
 Maracker: rapport de projet
=============================

.. raw:: latex

    \begin{abstract}

        Ce document décrit le déroulement du développement et de la mise en place
        d'une infrastructure visant à gérer un système distribué. Le système
        distribué a été mis en place sur un système GNU/Linux à l'aide
        des outils ZooKeeper, Mesos, Marathon, Chronos et Traefik.

        ZooKeeper est responsable de la synchronisation entre Mesos, Marathon et
        Chronos. Mesos, Marathon et Chronos s'occupent du partage des ressources
        (CPU, RAM, volumes) entre les différentes applications à excécuter
        sur le cluster de machines. Træfik gère l'exposition des applications
        (reverse-proxying) démarrées sur Marathon. De cette manière,
        les utilisateurs peuvent accéder aux applications web démarrées sur
        le cluster au-travers de leur navigateur.

        En plus de l'infrastructure mise en place, une API (Maracker)
        a été développée avec le framework Python Django.
        Elle remplit le rôle de registre d'applications et permet de demander
        le déploiement des applications sur le système distribué en utilisant
        l'API de Marathon.

        Toute l'infrastucture (ZooKeeper, Mesos, Marathon, Chronos, Træfik et
        Maracker) a été délivrée sous la forme de containers Docker.

        \begin{center}
          \textbf{Abstract}
        \end{center}

        This document describes the developpment process of an infrastructure.
        This infrastructure is responsible for managing a distributed system.
        The distributed system has been built using ZooKeeper, Mesos, Marathon,
        Chronos and Træfik on a GNU/Linux operating system.

        ZooKeeper is responsible for the synchronization between Mesos,
        Marathon and Chronos. Mesos, Marathon and Chronos take care of resources
        (CPU, RAM, volumes) management and sharing between the applications
        running on the cluster. Træfik does reverse-proxying onto the applications
        deployed on Marathon so that users can access them through their web
        browsers.

        On the top of that, an API called Maracker has been developped using
        Python Django framework. This API is used as an applications registery
        and allows users to ask applications deployment on the cluster using
        Marathon's API.

        The whole infrastructure (ZooKeeper, Mesos, Marathon, Chronos, Træefik
        and Maracker) has been delivered in the form of Docker containers.

        \end{abstract}

.. toctree::
   :maxdepth: 2
   :numbered:

Introduction
============

Ce document décrit la réalisation d'une API facilitant le déploiement
d'applications dans une infrastructure de type SaaS (Software as a Service)
dans le cadre d'un travail de bachelor en collaboration avec
le Centre hospitalier universitaire vaudois (*CHUV*) et la Haute école Arc
ingénierie (HE-ARC).

Contexte
~~~~~~~~

Le CHUV participe au projet Human Brain Project qui a pour but de mettre en
place une infrastructure de recherche pour différents domaines liés à
l’étude du cerveau.
Ce projet est décomposé en 12 sous-projets. L’équipe de développement du CHUV
s’occupe de la réalisation du sous-projet 8 (SP8):
Medical Informatics Platform (MIP).

Le premier but du SP8 est de proposer divers outils permettant de mieux
comprendre les différences et similitudes entre différentes maladies
du cerveau. Ces outils permettraient de mieux classifier, diagnostiquer
et traiter ces maladies en se basant sur une grande quantité de données
médicales anonymisées.

Son deuxième but est de rendre ces outils accessibles au-travers
d’une plateforme web. Quelques applications ont déjà été développées et
intégrées à la plateforme. Cependant il n’existe pas de moyen simple de
déployer une application tierce provenant des communautés de chercheurs en
neuroscience dans l’infrastructure existante.

La plateforme MIP repose déjà sur une infrastructure permettant de gérer
des services packagés dans des containers `Docker <https://www.docker.com/>`_
et répartis dans un cluster de machines (système distribué).
Les technologies de `Mesosphere <https://mesosphere.com/>`_
(`Mesos <http://mesos.apache.org/>`_  et
`Marathon <https://mesosphere.github.io/marathon/>`_) ont été utilisées pour
y parvenir.

.. raw:: latex

   \clearpage

Introduction aux systèmes distribués
------------------------------------

Afin de bien comprendre la problématique, il est préférable de commencer
par présenter le fonctionnement et l'intérêt des systèmes distribués.

Avant l'arrivée des applications web, l'architecture se limitait à
une couche d'application se superposant à celle du système d'exploitation
(OS) qui se superpose à l'hardware (:num:`Fig. #computer-arch-fig`).

.. _computer-arch-fig:

.. figure:: images/computer_architecture.png
   :width: 250px
   :align: center
   :alt: Architecture simple basée sur une application unique

   Architecture simple basée sur une application unique

Si on est dans le cas d'une application web, l'application peut
être une application web dite monolithique.
Cela signifie qu'elle est constituée d'un seul bloc et que
sa conception n'a pas été prévue pour la scinder en différentes
parties (front-end, back-end et éventuellement la base de données).

Les applications web devenant plus populaires, il a fallu déployer celles-ci
sur plusieurs machines de manière à ce qu'elles puissent supporter
le nombre croissant d'utilisateurs. On parle alors de haute
disponibilité et de scaling. Les machines sont donc organisées en clusters
(groupe de machines) et un load-balancer (répartiteur de charge) permet
de répartir les requêtes des utilisateurs sur les différentes machines
(:num:`Fig. #high-availability-fig`).

.. _high-availability-fig:

.. figure:: images/high_availability_architecture.png
   :width: 350px
   :align: center
   :alt: Architecture orientée haute disponibilité et «scalabilité»

   Architecture orientée haute disponibilité et «scalabilité»

Comme les données de certaines applications web pouvaient être également être
intéressante pour d'autres logiciels. Une nouvelle architecture a été adoptée
par les développeurs d'applications web: l'architecture orientée service
(Service Oriented Architecture) abrégée *SOA*.
Cette nouvelle architecture propose de donner un point d'entrée pour
les humains (des interfaces graphiques) et un point d'entrée pour
les machines fournissant des données sous différents formats
(:code:`JSON`, :code:`XML`, ...).
Afin d'adopter cette architecture les applications sont souvent découpées en
deux parties; une partie fournissant un front-end (utilisé par les humains)
et l'autre étant le service (utilisé par des logiciels).
Cela corresond à la figure (:num:`Fig. #soa-fig`).

.. _soa-fig:

.. figure:: images/soa.png
   :width: 350px
   :align: center
   :alt: Architecture orientée services

   Architecture orientée services

Le principal inconvénient de cette architecture est que cela demande plus de
travail de la part des administrateurs systèmes. Il y a deux
applications à maintenir mais aussi à exposer aux utilisateurs
et à sécuriser. Comme cela demande de plus en plus d'opération, il devient
nécessaire de s'abstraire du matériel et de faire du provisioning.
Cela consiste à créer
des machines virtuelles et d'en sauver leur image (snapshot) de manière
à pouvoir facilement en instancier une identique rapidement opérationnelle.
Une solution complémentaire est d'utiliser
un outil de déploiement automatisé comme `Ansible <https://www.ansible.com/>`_
qui s'exécute sur la machine virtuelle et installe toutes les dépendances.
Il devient donc possible de créer des machines virtuelles à la demande.
On parle d'infrastructure lorsque plusieurs machines virtuelles sont réparties
sur plusieurs machines physiques.
C'est de là qu'est né le terme Infrastructure as a Service (IaaS).

La virtualisation est la solution qui est la plus utilisée. Donnant ainsi
une architecture représentée par le :num:`Fig. #virtualization-fig`:

.. _virtualization-fig:

.. figure:: images/hardware_virtualization.png
   :width: 350px
   :align: center
   :alt: Architecture utilisant une solution de virtualisation

   Architecture utilisant une solution de virtualisation

Il existe de nombreuses solutions de virtualisation aujourd'hui.
Certaines sont moins gourmandes en ressources que d'autres.
Les plus utilisés sont `VMWare <https://www.vmware.com/fr.html>`_,
`Virtualbox <https://www.virtualbox.org/>`_ et
`KVM <https://www.linux-kvm.org/page/Main_Page>`_.

Si l'on désire faire du provisioning, il est possible d'utiliser
`Vagrant <https://www.vagrantup.com/>`_ en combinaison avec Ansible.

Cependant des questions concernant les problèmes de réseau se posent.
Comment gérer ces machines qui peuvent être créées
à la demande et gérer leurs configurations réseau pour que
les applications qu'elles hébergent soient accessibles aux utilisateurs?
Cela requiert que les développeurs connaissent l'ensemble de la stack.
Ce qui demande un investissement supplémentaire de leur part.
Une architecture basée sur des microservices a été proposée pour éviter
ce genre de problèmes. De cette manière, il est possible de déployer
plusieurs applications sur une même machine même si les applications
ne sont pas écrites dans le même langages.

.. _microservices-fig:

.. figure:: images/microservices.png
   :width: 350px
   :align: center
   :alt: Architecture basée microservices

   Architecture basée microservices

Dans la figure :num:`Fig. #microservices-fig`, les utilisateurs finaux
utilisent les applications et les applications utilisent les services.
Le problème de cette architecture est qu'il y un nombre important de services
à gérer. Il faut donc veiller à ce que les dépendances de chaque application
et service soient satisfaites. La solution trouvée pour résoudre ces problèmes
de dépendances a été d'utiliser des containers
(:num:`Fig. #containerized-microservices-fig`).

.. _containerized-microservices-fig:

.. figure:: images/containerized_microservices.png
   :width: 350px
   :align: center
   :alt: Architecture basée sur la conteneurisation de microservices

   Architecture basée sur la conteneurisation de microservices


Le principe d'un container consiste à partager le noyau (kernel)
du système hôte entre plusieurs processus faisant partie de l'espace utilisateur
(user space). Ces processus sont appelés des containers. Ce sont des processus
que l'on peut considérer comme des machines virtuelles dans le sens où
des programmes s'exécutent à l'intérieur. Chaque container est basé sur
l'image d'un système GNU/Linux. Les logiciels installés diffèrent donc
d'un container à un autre mais ils partagent tous le même noyau: celui du
système hôte.

Un container est normalement sans état (stateless) dans le sens où il ne
retrouve pas l'état dans lequel il était précédemment entre deux démarrages.
À chaque fois qu'il démarre, on se retrouve avec une machine «toute neuve».

Il est possible de rendre  un container stateful grâce au système de volumes.
Celui-ci
permet de partager des dossiers entre le système hôte et celui du container.
Dans le cas d'un container hébergeant une base de données par exemple,
un container stateful peut dumper la base de données régulièrement
dans un dossier partagé entre lui et le système hôte.
De cette manière on garde des backups de la base de
données sur le système hôte à son démarrage.
On peut ensuite rendre le container intelligent
pour qu'il vérifie la présence de dumps dans le dossier qu'il partage avec
l'hôte. S'il y en a, il les exécute et retrouve une base de données similaire
à celle avant son redémarrage.

Comme ils partagent le même noyau, les containers sont moins gourmands en
ressources que les machines virtuelles standards. On peut donc en lancer
plusieurs sur un même système hôte. C'est d'ailleurs l'intérêt des containers.
Ils sont plus légers que les machines virtuelles. Par exemple, on parle de 8 MB
pour une image basée sur Alpine Linux.

Un autre avantage des containers est qu'il est possible de créer sa propre
image. Un développeur qui crée une application peut donc créer un container
embarquant son application. La rendant ainsi plus facilement distribuable
car l'image contient toutes les dépendances requises par l'application
développée.

Il existe plusieurs solutions de conteneurisation; Docker, Singularity ou encore
LXC (Linux Container). Docker est une des solutions les plus populaires et
c'est celle qui est utilisée au CHUV pour packager ses microservices.

Dans cette architecture, le développeur n'a donc plus besoin de veiller
à ce que les dépendances soient installées sur sa machine virtuelle car
la machine virtuelle doit uniquement avoir la solution de conteneurisation
installée pour faire fonctionner son container. Les dépendances sont satisfaites
directement par l'image qui a été créée par le développeur pour son application.

L'inconvénient principal de cette architecture est que les machines virtuelles
hébergent de plus en plus de containers et que les opérateurs doivent planifier
les déploiements de ceux-ci sur les différentes machines à disposition
(en fonction des ressources demandées par chaque container). Les déploiements
sont donc bien plus simples qu'avant mais gérer les ressources à allouer pour
chaque container manuellement devient difficile même si le noyau Linux
possède quelques fonctionnalités pour le faire.
C'est pourquoi des outils d'orchestration de containers ont été développés.
Ceux-ci permettent d'automatiser cette procédure et donc de décharger
les opérateurs de cette responsabilité.
Si on utilise un outil d'orchestration de containers, l'architecture
prend alors la forme de la figure «:num:`Fig. #container-orch-revised-fig`.

.. _container-orch-revised-fig:

.. figure:: images/container_orchestration_revised.png
   :width: 350px
   :align: center
   :alt: Architecture utilisant un outil d'orchestration de containers

   Architecture utilisant un outil d'orchestration de containers

L'orchestration de containers est un processus automatisé qui vise à
planifier, coordonner et gérer les composants (containers) d'un système
complexe ainsi que les ressources qu'ils utilisent.

.. raw:: latex

    \clearpage

L'orchestration de containers consiste en trois types de tâches:

Gestion des services (Service Management):
    Ce groupe est responsable de définir ce qu'il faut faire avec
    chaque service une fois qu'il est déployé et comment en faire
    communiquer plusieurs entre eux. La vérification de la santé du service
    est également une tâche importante de ce groupe.

Planification (Scheduling):
    Ce type de tâche regroupe les décisions à prendre en termes de nombre
    d'instances de chaque service (scaling), à quel moment le(s) déployer,
    le mettre à jour, etc. Veiller à ce que certains services soient
    toujours déployés ensembles sur la même machine fait aussi partie
    de ce groupe de tâches.


Gestion des ressources (Resources Management):
    Les tâches de ce type consistent à veiller que les ressources (CPU, GPU,
    volumes, ports, IP) sont consommées de manière cohérente et distribuées
    comme désiré entre les différents containers.

Dépendant du contexte, d'autres fonctionnalités qui ne sont pas propres à
l'orchestration de containers comme la sécurité peuvent être exigées.

Une fois mise en place, une telle infrastructure permet de faire du PaaS
(Platform as a Service). Le PaaS vise à proposer une plateforme qui permet
aux développeurs de développer, déployer, tester et gérer leurs applications
sans devoir se soucier des problèmes liés à l'infrastructure sous-jacente.
Aujourd'hui ces applications sont souvent packagées dans des containers.
Microsoft Azure est un exemple de plateforme permettant aux développeurs
de déployer leurs containers.

.. raw:: latex

   \clearpage

.. _operating-system-fig:

.. figure:: images/operating_system.png
   :width: 300px
   :align: center
   :alt: Système d'exploitation

   Système d'exploitation

Finalement, en observant toutes ces couches, on peut comparer le fonctionnement
d'un tel environnement à un système d'exploitation
(:num:`Fig. #operating-system-fig` »). La couche contenant
les applications et services peut s'apparenter à des processus
s'exécutant dans l'espace utilisateur (user space).
La couche responsable de l'orchestration correspondrait à la couche de l'espace
kernel (aussi appelé system space). Les containers seraient vus comme
des microkernels (:num:`Fig. #distributed-operating-system-02-fig`).
La différence par rapport à un système d'exploitation standard est que
le système distribue toutes les tâches appartenant à l'espace utilisateur
sur différentes machines.

.. _distributed-operating-system-02-fig:

.. figure:: images/distributed_operating_system_02.png
   :width: 450px
   :align: center
   :alt: Système d'exploitation distribué

   Système d'exploitation distribué

Le principe de système distribué n'est pas récent. Des tentatives comme
`Plan 9 <https://en.wikipedia.org/wiki/Plan_9_from_Bell_Labs>`_
ont été développée avant l'existence des containers.
Seulement, l'utilisation de ce type de systèmes demandait de réécrire
complètement ses applications très souvent dans un langage de programmation
supportant la concurrence pas forcément connu du développeur.
Les solutions d'aujourd'hui ont permis de régler ce type de problèmes en partie
grâce à la conteneurisation des applications. Il n'est maintenant plus
nécessaire de réécrire son application et les nouveaux systèmes distribué
ne sont pas dépendants de l'OS choisi pour les nœuds du cluster ou du langage
utilisé pour écrire l'application.

Même s'il est appelé *système d'exploitation*, le système distribué est plutôt
vu comme une couche se superposant à l'OS existant de la machine hôte.
Il existe de nombreuses solutions permettant de mettre en place un système
d'exploitation plus ou moins complet.
Certaines comme `Docker Swarm <https://docs.docker.com/swarm/overview/>`_,
`ECS <https://aws.amazon.com/ecs/>`_ s'occupent uniquement
de l'orchestration des containers alors que d'autres solutions comme
`DC/OS <https://dcos.io/>`_ (DataCenter Operating System) issue de
la Mesosphere proposent un système d'exploitation distribué complet
avec une gestion des ressources assez fine et pouvant même supporter
des ressources comme des GPUs.

Le CHUV a d'ailleurs opté pour une solution de la Mesosphere mais
sans DC/OS qui contient plus de logiciels.
Leur système distribué est constitué de *Mesos*, *Marathon*, *ZooKeeper*
et *Chronos*.

.. Il existe déjà d'autres solutions de systèmes ditribués prévues pour
.. le domaine médical comme *cbrain*. Ce dernier étant prévu pour du calcul
.. distribué sur un cluster de HPC (High Performance Computer), il n'a pas
.. été retenu pour plusieurs raisons. La principale est que la plateforme
.. du MIP est prévue pour être déployée dans plusieurs hôpitaux à travers
.. l'Europe. Des clusters de HPC coûtant significativement plus cher que
.. des serveurs standards, une telle solution compliquerait
.. le déploiement de la plateforme dans chacun des hôpitaux.


Logiciels permettant de mettre en place un système distribué
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cette partie présente les différents logiciels utilisés dans l'infrastructure
du MIP. Elle a pour but d'expliquer le rôle de chaque logiciel dans l'infrastructure
ainsi que son fonctionnement.

Mesos
-----

Développé à l'université de Berkley, *Mesos* permet de gérer des clusters de
machines.
Ce logiciel propose plusieurs outils permettant l'isolation de CPU, de
mémoire et de fichiers. Utiliser un tel logiciel permet donc de partager
les ressources de l'infrastructure d'un data-center.
Il est utilisé pour la gestion de systèmes distribués de grandes
entreprises telles que Twitter, Airbnb, Apple ou encore Verizon.

Il permet de servir de kernel au data center et d'éviter de devoir créer
un cluster par application. On passe ainsi d'une forme traditionnelle
où on utilise un cluster par application (:num:`Fig. #no-mesos-cluster-fig`
à un cluster unique géré par Mesos (:num:`Fig. #mesos-kernel-fig`).

.. _no-mesos-cluster-fig:

.. figure:: images/cluster_without_mesos.png
   :width: 450px
   :align: center
   :alt: Clusters traditionnels sans Mesos

   Clusters traditionnels sans Mesos

.. _mesos-kernel-fig:

.. figure:: images/mesos_kernel.png
   :width: 450px
   :align: center
   :alt: Cluster géré avec Mesos

   Cluster géré avec Mesos

Deux types d'instances de Mesos fonctionnent conjointement; les instances
*primary* (mesos-master) et les instances *replica* (mesos-slave).
Si l'on veut interagir avec Mesos de manière programmatique,
il est nécessaire d'utiliser un framerwork. Celui-ci est composé
d'un scheduler (responsable de traiter les offres de ressources)
et un executor utilisable par les nœud replica pour réaliser une ou plusieurs
tâches du framework. Il existe des frameworks dans différents langages;
Spark pour Scala, Hadoop ou Storm pour Java et dpark pour Python.

Mesos supporte Docker et permet une isolation entre les tâches et les containers
devant les réaliser. Concernant son utilisation, Mesos propose un CLI
(Command Line Interface) et une interface web permettant son administration.

Dans le cadre de ce projet, *Marathon* est utilisé pour déployer
les services et les exécuter sur Mesos. *Chronos* est utilisé pour
les tâches uniques (lancement de scripts générant des sorties et se terminant
une fois la sortie générée). Ces deux logiciels seront présentés plus loin
dans ce document. Pour l'instant, on peut les voir comme des services
permettant de rendre l'exécution d'une application possible sur Mesos.
Cela est possible parce que ces deux logiciels respectent l'interface
de Mesos comme les frameworks présentés précédemment. Ils comportent
donc chacun un scheduler et un executor (capable d'exécuter un commande
ou lancer un container Docker).

.. raw:: latex

    \clearpage

L'interaction entre le framework (ou service comme Marathon ou Chronos),
le nœud primary et le nœud replica se fait de la manière suivante:

1. Le nœud replica notifie le nœud primary des ressources (nombre de CPUs,
   mémoire, etc.) dont il dispose.
2. Le nœud primary transmet l'offre de ressources du nœud replica au framework.
3. Le scheduler du framework répond au nœud primary en lui transmettant
   des tâches à réaliser par le nœud replica à disposition.
4. Le nœud primary transmet les tâches au nœud replica pour qu'il les exécute
   en utilisant les executors du framework.
   Si les tâches du framework n'utilisent pas toutes les ressources du
   nœud replica, celui-ci peut proposer le reste des ressources disponibles
   au framework ou à un autre framework.
5. Lorsqu'une tâche est terminée, le nœud replica recommence le cycle à
   l'étape 1.

Lorsque le nœud primary courant n'est plus disponible, les tâches en cours sur
le cluster continuent d'être exécutées sur les nœuds replica jusqu'à ce
qu'elles soient terminées.
Par contre, plus aucune ressource supplémentaire ne peut être allouée et
aucune nouvelle tâche ne peut être lancée.

Si on veut faire de la haute disponibilité, il est possible de démarrer
plusieurs nœuds primary et replica.
Au démarrage du cluster, *un seul* primary est choisi
comme *leader* parmi ceux disponibles.
Si le leader choisit n'est plus disponible, un nouveau est choisi parmi
les primary en fonctionnement. Ce système d'élection/réélection est réalisé
par le logiciel *ZooKeeper*.

ZooKeeper
---------

*ZooKeeper* permet de synchroniser différents services entre eux grâce à
un système de stockage clé-valeur implémenté
sous forme d'un système de fichiers. Les clients peuvent lire ou écrire
dans ce système de fichiers pour se transmettre des informations et ainsi
partager leurs configurations (accès aux serveurs de base de données, accès
aux serveurs HTTP, etc.). ZooKeeper est utilisé par des entreprises comme
Yahoo! et Reddit. Dans le cas de ce projet, il remplit les tâches suivantes
dans le cluster Mesos:

- Communication entre les différents primary pour élire le leader.
- Partage des informations du leader aux primary.
- Détection des autres agents compatibles avec Mesos (Marathon, Chronos,
  Hadoop, etc.)

Pour plus d'information veuillez consulter
la `documentation ZooKeeper <http://zookeeper.apache.org/doc/trunk/recipes.html#sc_leaderElection>`_.

Avant de démarrer, le serveur ZooKeeper doit être initialisé avec un ID.
Par exemple, pour l'initialiser avec un l'ID *1*, il suffit de lancer la
commande :code:`sudo -u zookeeper zookeeper-server-initialize --myid=1`.
Cet ID doit toujours être un nombre entier unique.
Il est utilisé pour différencier chaque serveur ZooKeeper.
Cela est surtout important lorsque plusieurs serveurs ZooKeeper fonctionnent
dans un cluster pour permettre de la haute disponibilité.

Une fois initialisé, le serveur peut être démarré. Comme il se comporte
comme un service sur UNIX, il suffit de lancer la commande
:code:`sudo service zookeeper-server start`. On peut l'appeler avec
:code:`enable` si l'on veut que le serveur démarre au boot de
la machine et ainsi éviter de devoir le démarrer manuellement.
On peut le stopper avec :code:`stop`.

On peut interagir avec ZooKeeper au-travers de son client à l'aide de
la commande :code:`zookeeper-client`.

Marathon
--------

**Marathon** est un outil de PaaS (Platform as a Service).
C'est une surcouche visant à faciliter l'utilisation de Mesos. Il permet de
faire de l'orchestration de containers et faire du scaling (gestion
des ressources
et démarrage/arrêt d'applications) pour différents services.
Ces services peuvent être contenus dans des containers Docker ou
directement accessibles en ligne de commande. Dans le deuxième cas,
il est nécessaire que ces services soient installés sur tous
les nœuds replica du cluster.
Marathon propose une interface web d'administration et une *API REST*
implémentée en *Scala*.

C'est cette API qui sera utilisée pour la réalisation de ce projet.
Par exemple, pour instancier un simple serveur HTTP en Python,
il suffit d'envoyer le fichier *json* suivant à l'API:

.. literalinclude:: examples/test.json
   :language: json

Toute application instanciée doit avoir un identifiant unique défini par
l'utilisateur (ici :code:`test`). Si l'application se lance au-travers
d'une commande, il faut spécifier celle-ci avec la clé :code:`cmd`.
Si la commande prend des ports en arguments pour rendre l'application
accessible, il est possible d'utiliser les variables :code:`$PORT0`,
:code:`$PORT1`, etc. pour déléguer le choix du port à Marathon.
Un port libre sera choisi aléatoirement. On peut ensuite définir les ressources
dont l'application à déployer a besoin (clés :code:`cpus` et :code:`mem`).
Le minimum pour la clé :code:`cpus` est 0.1 et le minimum pour la clé
:code:`mem` est 32. La mémoire est quantifié en *megabytes* (MB).
Les ressources spécifiées sont la quantité de ressources par instance.
Il faut également spécifier le nombre d'instances à l'aide de
la clé :code:`instances`.
Si l'on veut modifier une application déjà déployée, il suffit de faire
une requête :code:`PUT` sur l'API avec les champs modifiés
(exemple: le nombre d'instances). Marathon opérera les modifications
en redéployant l'application.

.. raw:: latex

   \clearpage

Il est également possible d'instancier des containers Docker avec Marathon.
En voici un exemple:

.. literalinclude:: examples/whoami.json
   :language: json

Les clés `id`, `cpus`, `mem` et `instances` remplissent le même rôle que dans
l'exemple précédent. La clé `container` permet de décrire à Marathon quel
container doit être utilisé. La clé `type` décrit le *containerizer* à
utiliser pour démarrer le container (ici `DOCKER`). Normalement,
la clé `type` n'est pas obligatoire lorsque l'on utilise Docker comme
containerizer car c'est sa valeur par défaut.
La clé `docker` contient un object décrivant l'image à utiliser dans la clé
`image` (ici `emilevauge/whoami`). Cette image d'exemple est un simple serveur web
affichant une page d'index contenant des informations sur ce serveur.
La clé `network` spécifie le comportement que le container aura sur le réseau.
La valeur `BRIDGE` connectera le container au sous-réseau créé par Docker
(en général `172.17.0.1/16`). Si la configuration réseau est en `HOST`,
le container partage la même interface réseau que la machine hôte.
Il n'y a donc plus d'isolation entre le container et la machine hôte
sur laquelle il a été déployé du point de vue du réseau.

Chronos
-------

*Chronos* est l'équivalent du cron de Linux pour Mesos. Il peut être
utilisé pour planifier des tâches au-travers de clusters Mesos et gérer des
dépendances entre eux de manière plus ou moins intelligente.

Une utilisation possible de Chronos pourrait consister à redémarrer
des services de manière quotidienne afin de relancer ceux qui seraient
éventuellement bloqués. On pourrait aussi imaginer récupérer des logs et
des dumps de base de données et les transférer sur une autre machine
pour faire des backups.

Une autre utilisation possible est de lancer des tâches qui ne
doivent être lancées qu'une seule fois. Un cas rentrant dans
ce type de tâches est le lancement d'un script analysant
une grande quantité de données (dans une base de données ou un fichier)
pour en génèrer un résultat en sortie dans un fichier dans un répertoire.

Résumé de l'architecture présentée
----------------------------------

Le diagramme d'architecture dans la figure :num:`Fig.#marathon-arch-fig`
montre comment peuvent être déployés les différents composants du système
distribué en utilisant les technologies présentées précédemment.

.. _marathon-arch-fig:

.. figure:: images/marathon_architecture.png
   :align: center
   :width: 350px
   :alt: Architecture Mesos, Marathon, Chronos et ZooKeeper

   Architecture Mesos, Marathon, Chronos et ZooKeeper


Dans ce cas, plusieurs instances de ZooKeeper, Mesos-Master et Marathon
fonctionnent afin de garantir de la haute disponibilité. On peut imaginer
qu'il s'agisse de trois machines embarquant chacune une instance
de ZooKeeper, Mesos-Master et Marathon.

Plus bas, on peut voir que neuf machines embarquent une instance de
Mesos-Slave. Chaque nœud s'est fait attribuer une ou plusieurs tâches
par le Mesos-Master *leader* du cluster à l'exception d'un seul.

Les tâches en oranges sont celles dont l'exécution a été demandée par Marathon.
Celles en bleu sont celles dont l'exécution a été demandée par Chronos.
On peut constater que deux instances de Chronos ont été lancées depuis
Marathon. Lancer Chronos depuis Marathon est intéressant car il sera
automatiquement redémarré par Marathon s'il cesse soudainement de fonctionner.
Scaler Chronos à deux instances permet également de faire de la haute
disponibilité. S'il est lancé depuis Marathon, Chronos peut s'exécuter de deux
manières différentes.
Soit il est installé sur chaque nœud du cluster et on spécifie à Marathon
la commande nécessaire à son lancement.
Soit on demande son lancement en spécifiant une image Docker comme
`mesosphere/chronos <https://hub.docker.com/r/mesosphere/chronos/>`_.
Il en est de même pour les autres tâches comme `JBOSS`, `Rails`,
`Jetty Service`, etc.

Problématiques non-résolues par les solutions de systèmes distribués
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Même si les nouveaux systèmes d'exploitation distribués facilitent
le déploiement d'applications et de services sur un ou plusieurs clusters,
il est nécessaire de mettre en place d'autres fonctionnalités
qu'ils ne proposent pas. Pour donner quelques exemples; la sécurité
(authentification, permission, ...), un catalogue de services
disponibles sur la plateforme (récupérer une application à partir d'une liste
et la déployer sur le cluster), un reverse proxy ou encore un outil
d'autoscaling.

Objectifs
=========

.. figure:: images/170718-schema_simplifie.png
   :align: center
   :alt: Schéma d'architecture simplifé

   Schéma d'architecture simplifié

Marathon propose une API REST permettant d'instancier des applications et
d'en gérer le nombre d'instances. Le but du travail consiste à réaliser
une API permettant de déployer des applications (web services) packagées
dans des containers Docker sur Marathon.
Cette API serait donc une surcouche à Marathon.

Une des fonctionnalités supplémentaires apportées par l'API serait de proposer
un catalogue de services (nom, description, lien vers le code source, etc.).

Pour qu'une application soit déployable, il faudrait que les métadonnées
(LABELS) contenues dans le Dockerfile de celle-ci décrivent les ressources
(CPU et mémoire) dont elle a besoin.

Si cette partie est réalisée, le développeur pourra rechercher et mettre
en œuvre une solution permettant d'exposer les applications instanciées
dans Marathon. Des solutions open source existantes comme *Træfik* et *vamp*
peuvent constituer de bonnes pistes pour régler cette problématique.

S'il reste du temps, le développeur pourra développer un frontend
proposant à l'utilisateur une liste d'applications en disponibles et
en exécution. Il pourra ensuite les tester grâces à des :code:`<iframe>`.

On peut donc résumer les objectifs de la manière suivante:

1. Mettre en place une base de données PostgreSQL répertoriant différentes
   applications disponibles et déployables dans l’infrastructure.
   Cette base de données contiendrait plusieurs informations;
   nom de l’image Docker, nom de l’application, description de l’application
   et des informations de déploiement (mémoire, CPU) nécessaires au
   fonctionnement de l'application.
2. Développer une API REST permettant de faire du CRUD sur la base
   de données (ajout/suppression/modification). L’API permettrait
   également de demander le démarrage/arrêt d’une application
   particulière à l’aide de l’API de Marathon.
3. Tester voire mettre en œuvre une solution permettant d’exposer
   les applications déployées avec Marathon aux utilisateurs.
4. Réaliser un démonstrateur permettant de tester l’API et éventuellement
   afficher les applications déployables de manière similaire au
   `Dockstore <https://dockstore.org/>`_.
   Les applications en cours d’exécution pourraient être affichées à
   l’aide d’:code:`<iframe>`.


Les objectifs *1* et *2* sont considérés comme objectifs primaires et
constituent le coeur du travail. Les objectifs *3* et *4* sont
des objectifs secondaires.

Choix des technologies
======================

Cette partie décrit les différentes technologies qui ont été utilisées
pour mettre en place un environnement de test et développer les différentes
fonctionnalités citées précédemment dans les objectifs.

Environnement de test
~~~~~~~~~~~~~~~~~~~~~

Les technologies utilisées pour mettre en place le cluster de machines sont
celles du MIP; Mesos, ZooKeeper, Marathon et Chronos. Comme les dépôts mis
à disposition n'étaient pas fonctionnels pour une personne externe au SP8,
le développeur a dû mettre en place un cluster lui-même.

.. figure:: images/mesos-cluster-test.png
   :width: 350px
   :align: center
   :alt: Premier cluster de test

   Premier cluster de test

Deux approches ont été adoptées. La première a visé à mettre en place
un cluster de machines en se basant sur les cours mis à disposition par
la communauté de Mesosphere. Cette approche a consisté à mettre en place
ZooKeeper, Mesos puis Marathon et finalement Chronos sur une machine virtuelle.
Le système de la machine virtuelle est un système GNU/Linux
`CentOS <https://www.centos.org/>`_ (dérivé de la distribution
`Red Hat <https://www.redhat.com/en>`_).
Une fois ces logiciels mis en place, il a été possible de passer d'un cluster
d'une machine à un cluster de quatre machines;
une embarquant Mesos Master/Slave, Marathon, ZooKeeper et Chronos et
les trois autres embarquant Mesos Slave.

Le but de cette approche a été de permettre au développeur de prendre en main
et comprendre comment chaque composant interagit avec les autres.
Vagrant a été utilisé en combinaison avec KVM pour la gestion des machines
virtuelles constituant le cluster.

Vagrant est un outil open source permettant de créer et gérer des machines
virtuelles. Il fonctionne avec un script *Ruby* nommé `Vagrantfile`.
Ce script décrit les propriétés de la machine virtuelle telles que
la distribution utilisée, son nom, sa quantité de RAM, le nombre de CPU
qu'elle possède et sa configuration réseau.

On peut créer un `Vagrantfile` facilement grâce à la commande
:code:`vagrant init centos/7` qui crée un `Vagrantfile` basé sur une machine
CentOS par exemple. On peut ensuite lancer la machine virtuelle en se plaçant
dans le dossier contenant le `Vagrantfile` et en utilisant la commande
:code:`vagrant up`. On peut ensuite se connecter à la machine virtuelle en ssh
grâce à la commande :code:`vagrant ssh`. On peut éteindre la machine virtuelle
démarrée avec la commande :code:`vagrant halt` ou :code:`vagrant destroy`
si on désire effacer complètement la machine virtuelle.

Vagrant a besoin d'un hyperviseur pour fonctionner. Il supporte `Virtualbox`,
`Docker` et également `KVM`/`libvirt`.
Il est généralement utilisé avec Virtualbox mais il semble que KVM soit
la solution à privilégier. Utilisé par DigitalOcean et Linode, KVM est un bon
compromis entre performance et sécurité.

Un des avantages de Vagrant est qu'il peut être utilisé conjointement
à Ansible. Cela permet notamment de faire du provisioning et de pouvoir
recréer facilement un cluster de machine par exemple.

`Ansible` est un outil de déploiement automatisé et de provisioning.
Lors du déploiement, une machine est responsable de
l'orchestration du déploiement et commande les machines où doivent être
déployés les services.

.. raw:: latex

    \clearpage

Ansible s'utilise généralement avec `Ansible Playbook` qui permet d'exécuter
Ansible pour mettre en place des services grâce à des scripts appelés
*playbooks*. Voici un exemple de playbook permettant de mettre en place
un nœud replica pour un cluster mesos:

.. literalinclude:: examples/playbook.yml
   :language: yaml

Dans chaque playbook, il est nécessaire de définir la machine (ou groupe de
machines) sur laquelle on désire déployer nos services (ici :code:`nodes`
qui correspond au groupe de nœuds replica du cluster).
Il est également nécessaire de spécifier l'utilisateur qui s'y connecte
(:code:`vagrant` comme il s'agit d'une machine Vagrant).
Si certaines commandes doivent être lancées en tant que super utilisateur,
il faut activer cette fonctionnalité et définir quelle commande permet de
changer d'utilisateur. Dans notre cas, on utilise la commande :code:`sudo`.
Une fois ces quatre variables définies, on peut définir les tâches (*tasks*)
à réaliser.
Celles-ci seront exécutées l'une après l'autre. Chaque :code:`task` a un nom
décrivant son but et une action. Il existe différents type d'actions:

- :code:`template`: Permet de copier des fichiers de la machine hôte
  à la machine distante. Cette commande utilise le moteur de template
  `jinja <http://jinja.pocoo.org/>`_ et il est possible de lui passer
  des variables. Cela permet de personnaliser des fichiers de configurations
  par exemple.
- :code:`apt`, :code:`yum`, ... : Permet d'installer des packages facilement.
  Il existe des actions adaptées pour beaucoup de distributions Linux et
  langages comme *ruby* (:code:`bundler`) et *python* (:code:`pip`).
- :code:`shell`: Permet de lancer une commande dans le shell.

Ansible est donc un outil de déploiement puissant. Il l'est encore plus
lorsqu'il est combiné avec Vagrant car il permet de recréer un cluster
de machines en quelques minutes. Le cluster mis en place avec cette approche
est disponible dans le dossier `mesos-cluster-test`.

Le problème de la première approche a été son besoin assez important
en ressources. Elle a été utile pour comprendre comment fonctionnent et
se configurent les différents composants de l'infrastructure mais ne
permettait pas de tester l'API qui serait développée avec ce cluster.

C'est pourquoi une seconde solution utilisant Docker et *Docker Compose*
a été mise en place. Docker Compose fonctionne avec un fichier `YAML`
décrivant chaque service à démarrer ainsi que l'image Docker à utiliser pour
chaque service (container).

.. _test-cluster-code:

.. code-block:: yaml

    version: '2'

    services:
      zoo1:
        image: zookeeper:3.4
        network_mode: host
        ports:
           - 2181:2181

      mesos-master:
        image: mesosphere/mesos-master:1.3.0
        network_mode: host
        environment:
          - MESOS_CLUSTER=local
          - MESOS_ZK=zk://127.0.0.1:2181/mesos
          - MESOS_IP=127.0.0.1
          - MESOS_QUORUM=1
          - MESOS_WORK_DIR=/var/lib/mesos

      mesos-slave:
        image: mesosphere/mesos-slave:1.3.0
        network_mode: host
        privileged: true
        environment:
          - MESOS_PORT=5051
          - MESOS_MASTER=zk://127.0.0.1:2181/mesos
          - MESOS_IP=127.0.0.1
          - MESOS_CONTAINERIZERS=docker,mesos
          - MESOS_WORK_DIR=/var/lib/mesos
          - MESOS_SWITCH_USER=0
        volumes:
          - /sys/fs/cgroup:/sys/fs/cgroup
          - /usr/bin/docker:/usr/bin/docker.so
          - /var/run/docker.sock:/var/run/docker.sock

L'exemple de code déclare trois services; `zoo1` (ZooKeeper),
`mesos-master` (Mesos Master) et `mesos-slave` (Mesos Slave).
Chaque service utilise une image Docker disponible sur
`Docker Hub <https://hub.docker.com/>`_. Docker se charge lui-même du
téléchargement des images si elles ne sont pas présentes sur la machine.

`network_mode` définit le comportement réseau des containers.
Les services sont tous en `HOST` car Mesos ne fonctionne pas en mode `BRIDGE`
sans rencontrer des problèmes de configuration. Le principal problème est
que l'interface du mode  `BRIDGE` n'est pas suffisamment rapide pour que
les échanges entre Mesos, ZooKeeper, Chronos et Marathon se fassent
correctement.

La clé `environment` permet de définir les variables d'environnement pour
le container. Pour le service `mesos-master`, `MESOS_ZK` contient l'adresse
à laquelle les nœuds Mesos peuvent contacter ZooKeeper et s'échanger
des informations.

`volumes` permet de partager des dossiers entre le container et
la machine hôte.

Si des ports du container doivent être exposés, il est nécessaire d'utiliser
la clé `port`. En mode `HOST`, il faut respecter la syntaxe
`<port_hôte>:<port_container>`.

En plus d'être plus léger, le cluster démarre bien plus rapidement
qu'avec la solution précédente avec Ansible (une minute avec Docker
contre douze avec Vagrant et Ansible). De plus cette solution est plus
facilement partageable. Elle a d'ailleurs été partagée avec un collègue
dont le travail de bachelor s'insérait dans cette infrastructure.

Environnement de développement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Le développeur a été laissé libre de choisir le langage d'implémentation de
l'API parmi Python, Go, Scala ou Java. Python a été choisi parce que c'est
un des langages avec lequel il est le plus à l'aise. De plus, il propose
déjà `Django <https://www.djangoproject.com/>`_ comme framework web.
Combiné à `Django REST framework <http://www.django-rest-framework.org/>`_,
le développement d'une API est accéléré.

Comme Docker est un impératif nécessaire pour faire fonctionner l'environnement
de test, le système d'exploitation choisi pour le développement est Linux.

Gestion de projet
=================

Cette partie décrit la manière dont le projet a été géré au niveau de
sa planification et de la gestion des risques.

Planification
~~~~~~~~~~~~~

La première phase du projet (10 premières semaines) a consisté à prendre
en main les outils et technologies présentées précédemment; Vagrant,
Mesosphere (Mesos et Marathon), le système d'exploitation
CentOS et Ansible.

La seconde phase (à 100%) a consisté à préciser les besoins du mandant et de
mettre en place la base de données, l'API puis d'exposer les services
instanciés dans Marathon avec la solution Træfik.
Le développement d'un frontend était prévu mais n'a pas pu être réalisé
à cause des imprévus (changement des besoins du mandant) et du manque de temps.

À défaut de se lancer directement dans l'implémentation d'une solution,
cette approche a permis de mieux comprendre la problématique.
Cette dernière n'était pas évidente à comprendre car complexe pour
un développeur qui n'a pas de connaissances préalables en systèmes distribués
et en PaaS.

La première et la seconde version de la planification sont consultables dans
les annexes (dossier `annexes`). Aucune version supplémentaire n'a été faite
comme la méthodologie de développement choisie était itérative.

.. raw:: latex

    \clearpage

Définition et gestion des risques
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plusieurs risques ont été identifiés au début du projet. Le premier a été
les nombreuses technologies à prendre en main. Beaucoup d'outils ont dû être
pris en main et cela a nécessité plusieurs semaines. La solution proposée
pour ce problème était de réorienter le projet vers des objectifs plus simples.

Un second risque identifié a été le changement de la spécification en cours de
projet. La solution proposé a été de d'abord développer ce qui avait été convenu
dans le cahier des charges et d'ensuite réaliser les modifications si il restait
du temps.

Conception
==========

Architecture générale
~~~~~~~~~~~~~~~~~~~~~

.. _final-arch-fig:

.. figure:: images/architecture_schema.png
   :width: 550px
   :align: center
   :alt: Schéma d'architecture finale

   Schéma d'architecture finale

La figure :num:`Fig. #final-arch-fig`, représente ce qui a été mis en place
au moment du rendu. Les différents composants sont des containers Docker.
Ces containers sont coloriés de deux manières. Soit en bleu foncé s'il s'agit
d'un container embarquant un service nécessaire au fonctionnement
de l'infrastructure, soit en bleu clair s'il s'agit d'un container déployé
par Mesos.

L'utilisateur peut donc interagir avec l'API implémentée
en Python pour ajouter/modifier/supprimer des services. Ces services sont
principalement des applications de visualisation développées à l'aide de
frameworks ou bibliothèques comme Angular, React, D3, Bokeh, etc.

Les informations concernant le déploiement (mémoire, CPU, ports à exposer,
image Docker à utiliser) sont stockées dans la base de données.

L'utilisateur peut ensuite demander le déploiement d'un service au-travers de
l'API. Cela demande à l'API de communiquer avec le container embarquant Marathon
pour demander le déploiement de l'application spécifiée par l'utilisateur.

Le container Marathon transmet la demande de création de la tâche au container
contenant Mesos-Master (primary) qui chargera le container Mesos-Slave (replica)
d'exécuter la tâche et d'instancier le container embarquant le service demandé.
Si l'image Docker du service n'est pas disponible sur le replica, elle est
téléchargée avant l'instanciation du container.

Une fois que le container du service est démarré, Marathon le signale dans son
`bus d'évènement <https://mesosphere.github.io/marathon/docs/event-bus.html>`_.
C'est ce flux qui est utilisé par `Træfik` pour être notifié des démarrages/arrêts
des services. Il peut ensuite examiner les métadonnées du service
comme les `labels <https://mesosphere.com/blog/2016/01/12/improving-operational-analytics-with-marathon-labels/>`_.
Ces labels permettent de spécifier à Træfik comment exposer le service.
`traefik.frontend.rule` permet de définir à quel nom de domaine le service
sera accessible par exemple.

.. _traefik-internal-fig:

.. figure:: images/traefik_internal.png
   :align: center
   :alt: Fonctionnement interne de Træfik

   Fonctionnement interne de Træfik

Dans le cas de la figure :num:`Fig.#traefik-internal-fig`,
plusieurs microservices ont été déployés; `api`, `web` et `backoffice`
(scalé en trois instances).
Chaque microservice se voit attribué un URL (ici `api.domain.com`,
`domain.com/web` et `backoffice.domain.com`). Ces URL sont utilisés
pour créer un frontend par service. Ces frontend sont un ensemble de règles
qui se chargent de faire la correspondance entre les points d'entrée et
les backends.
Un backend peut-être constitué d'une ou plusieurs instances de serveurs
embarquant le même service.

Træefik traite donc les requêtes qu'il reçoit de la manière suivante:

1. Il vérifie que l'hôte (HOST) demandé existe dans la liste des frontends.
   Il répondra à l'utilisateur avec un code HTTP `404` si ce n'est pas le cas.
   La requête est transmis au backend associé au frontend.
2. Si ce backend est constitué de plusieurs serveurs, un serveur est choisit
   selon une règle qui dépend de sa configuration. Le comportement par défaut
   est d'en choisir un aléatoirement.

L'avantage d'utiliser Træfik est que l'administrateur de l'infrastructure
n'a pas besoin de gérer les configurations du reverse-proxy lui-même
(virtual hosts, ports d'écoute, redirection de HTTP à HTTPS). Træfik s'en charge
directement.

Dans le cas présent, toute communication en HTTP (port `80`) avec
les points d'entrée pour chaque microservice est redirigée sur
le port HTTPS (`443`) afin de chiffrer les communications entre
les utilisateurs et les microservices.

Træfik possède d'autres fonctionnalités telles que du load-balancing,
des healthchecks. De plus, il supporte de nombreux orchestreurs de containers
en plus de Marathon comme `Kubernetes <https://kubernetes.io/>`_
ou Docker Swarm. Ces fonctionnalités supplémentaires ne seront pas utilisées
dans le cadre de ce projet.

Base de données
~~~~~~~~~~~~~~~

Cette section décrit comment la base de données a été conçue.

Au moment de la conception de la base de données,
`Boutiques <http://boutiques.github.io/>`_
a été proposé par le mandant. Boutiques est une solution pour décrire
une application et la manière dont elle s'utilise. L'application est décrite
à l'aide d'un fichier JSON.

Cette spécification n'a pas été utilisée car elle semblait trop contraignante
et ne pas correspondre aux besoins du projet pour plusieurs raisons:

- Boutiques est prévu pour exécuter des workflows. Les workflows sont
  des applications prenant en entrée des paramètres et générant des fichiers
  en sortie. Lorsque la tâche a été réalisée, l'application s'arrête.
  Cela ne correspond pas à l'exécution d'un service.
- Les ports à exposer pour accéder au service ne sont pas gérés par
  cette spécification.

La discussion sur ce sujet est disponible dans
`cette issue <https://github.com/groovytron/maracker/issues/10>`_.

Cela a pu montrer que deux types d'application peuvent être lancés;
des services et des workflows. Les workflows étant des tâches réalisées
une seule fois, elle ne peuvent pas être déployées sur Marathon qui est
fait pour exécuter et réssuciter les services si ils venaient à s'arrêter.
Ces workflows doivent être démarrés dans Chronos et non dans Marathon.

Le premier schéma entités - relation qui a permis le développement de
la première base de données est celui de la figure
:num:`Fig. #schema-entity-relationship-01`.

.. _schema-entity-relationship-01:

.. figure:: images/entity_relationship_schema_01.png
   :width: 450px
   :align: center
   :alt: Premier schéma entités - relations

   Premier schéma entités - relations

Finalement, comme le support de Boutiques n'a pas été retenu dans le cadre
du projet, un second schéma entités - relations a été réalisé en prévoyant
un support de Boutiques plus tard si le projet est repris
(:num:`Fig. #schema-entity-relationship-02`).

.. _schema-entity-relationship-02:

.. figure:: images/entity_relationship_schema_02.png
   :align: center
   :alt: Second schéma entités - relations

   Second schéma entités - relations

Supporter Boutiques demanderait de supporter l'API de Chronos pour exécuter
ce type d'applications. Cela ne figurant pas dans le cahier des charges,
cette fonctionnalité n'a pas été développée.

Architecture logicielle
~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: images/mvt_schema.png
   :align: center
   :alt: Architecture Modèle - Vue - Template

   Architecture Modèle - Vue - Template

Comme Django a été utilisé pour réaliser l'API. Une architecture *MVT*
(Modèle - Vue - Template) a été utilisée car elle est imposée par
ce framework. Même si la nomination change, le fonctionnement est
le même que celui d'une architecture *MVC* (Modèle - Vue - Contrôleur).

Le modèle est responsable de la communication avec la base de données.
Le template se charge de la présentation des données à l'utilisateur
La vue s'occupe de récupérer les données à l'aide du modèle et d'ensuite
appeler le template en lui transmettant les données du modèle.

Lorsque l'utilisateur veut afficher la liste des applications en utilisant
l'API à l'adresse http://api.com/apps, le framework s'occupe du routing.
Si la route `/apps` existe, la requête est transmise à la vue associée
à cette route.
La vue va ensuite rechercher des informations dans la base de données
en se servant du modèle. Une fois récupéré, le résultat est passé au template
pour présenter les données à l'utilisateur sous la forme d'une page web.

Comme le but du projet est de développer une API, seules les parties modèle et
vue ont été utilisées.

Les routes, les modèles et les vues sont définis respectivement dans
les fichiers `maracker/marackerapi/urls.py`, `maracker/marackerapi/models.py` et
`maracker/marackerapi/views.py` du répertoire contenant le code source du
projet.

Trois modèles ont été créés à partir du schéma entités - relations
(:num:`Fig. #schema-entity-relationship-02`); `MarackerApplication`,
`DockerContainer` et `MarathonConfiguration`:

Implémentation
==============

Routes
~~~~~~

Voici les différentes routes de l'API et les actions que chacune effectue:

- `/apps`:

  - `GET`: Retourne un tableau JSON contenant toutes les applications
    répertoriées dans la base de données.

  - `POST`: Permet de créer une application.

- `/apps/<id>` et `/apps/<name>`: Permet d'effectuer des opérations CRUD
  sur une application particulière. La sélection de l'application peut
  se faire soit par son `id`, soit par son nom (`name`).

  - `GET`: Retourne un objet JSON contenant les informations relatives à
    l'application.

  - `PUT`: Modifie les informations de l'application.

  - `DELETE`: Supprime l'application spécifiée.

- `/container/docker/<id>`: Comportement identique à la route `/apps/<id>`
  sauf qu'elle opère sur les containers.

- `/marathon-config/<id>`: Comportement identique à la route `/apps/<id>`
  sauf qu'elle opère sur les configurations Marathon.

- `/deploy/<id>`: Permet de déployer sur Marathon l'application associée
  à la configuration Marathon spécifiée par le paramètre `id`.
  Seule la méthode HTTP `POST` est autorisée pour cette route.

- `/delete/<id>`: Permet de supprimer de Marathon l'application correspondant
  à la configuration Marathon spécifiée par le paramètre `id`.
  Seule la méthode HTTP `POST` est autorisée pour cette route.

API
~~~

L'API a été développée à l'aide de *Django REST framework*. Ce framework a été
utilisé parce qu'il facilite la sérialisation des modèles en JSON. Il permet aussi de
simplifier la création des vues.

De cette manière, développer une fonctionnalité devient plus simple. Il suffit de
suivre la démarche suivante:

1. Créer les modèles.
2. Créer les sérialiseurs associées aux modèles.
   (fichier `maracker/marackerapi/serializers.py`)
3. Créer les vues relatives à la fonctionnalité.
4. Créer la/les route(s) et la/les associer aux vues créées précédemment.

Même si Django REST framework a facilité la création
des fonctionnalités, il a fallu modifier les sérialiseurs de manière à ce
qu'ils gèrent les relations.

Effectivement, le comportement par défaut des sérialiseurs est
sérialiser/désérialiser les modèles sans leurs relations.
Par exemple, le modèle `MarackerApplication` possède un ou aucun
`DockerContainer` et aucun ou plusieurs `MarathonConfiguration`.

L'API a été pensée pour que l'utilisateur n'aie pas à faire trois requêtes
pour savoir à quelle `MarackerApplication` appartient chaque
`MarathonConfiguration`. Les sérialiseurs ont été modifiés de manière à
ce que lorsque que l'utilisateur demande la liste des applications,
ils les obtiennent avec leurs containers et configuration Marathon respectifs.

.. raw:: latex

    \clearpage

Voici un exemple présentant le résultat d'une requête sur la route `/apps`:

.. code-block:: json

    [
        {
            "id": 15,
            "name": "simple-webapp",
            "description": "simple web application from docker-training",
            "command": "",
            "vcs_url": "",
            "docker_container": {
                "id": 15,
                "image": "pschiffe/keycloak-demo-web-app",
                "ports": [
                    5000
                ]
            },
            "marathon_configs": [
                {
                    "id": 15,
                    "cpu": "1.0",
                    "memory": 64,
                    "args": "",
                    "env_vars": {}
                }
            ]
        }
   ]

Dans l'exemple ci-dessus, le tableau retourné contient une seule application.
On constate que toutes les informations relatives à l'application
`simple-webapp` sont accessibles en une seule requête.

`docker_container` contient le container associé à l'application. Si aucun
container n'est associé à cette application, cette clé contient la valeur
`null`.

`marathon_configs` est un tableau contenant des objets JSON représentant
les configurations Marathon associées à l'application.

Procéder de cette manière permet de faciliter les actions CRUD sur
les containers et les configurations liés à l'application on a directement
accès à leurs `id`.

.. raw:: latex

    \clearpage

Si l'on désire créer un service, il est nécessaire de faire une requête `POST`
sur la route `/apps`. Voici un exemple de contenu JSON permettant de déployer
un service `Nginx`:

.. literalinclude:: examples/maracker/docker-nginx.json
   :language: json

Cela correspond à un service packagé dans un container Docker dont l'image est
`nginx` et le port `80` doit être exposé.
Pour être exécuté, ce service a besoin d'utiliser un CPU et `64 MB` de RAM.
Ce sont les ressources qui seront demandées à Marathon au moment du déploiement.

Si l'insertion du service dans la base de données réussi, le même JSON est
retourné avec des clés `id` en plus.

.. code-block:: json

    {
      "id": 6,
      "name": "nginx-test",
      "description": "simple nginx container",
      "docker_container": {
        "id": 4,
        "type": "docker",
        "image": "nginx",
        "ports": [80]
      },
      "marathon_configs": [{
        "id": 12,
        "cpu": 1,
        "memory": 64
      }]
    }

Ces clés contiennent les identifiants de chaque modèle lié au service. Ici on
peut voir que le service créé possède l'id `6`, son container l'id `4` et
sa configuration marathon l'id `12`.

On peut donc obtenir les information du service à la route `/apps/6`.
On peut également afficher/modifier/supprimer son container docker
en faisant une requête `GET` sur la route `/container/docker/4`.
On peut effectuer le même type d'opérations sur la configuration Marathon du
service en utilisant la route `/marathon-config/12`.
Le déploiement de cette configuration peut être fait en effectuant une requête
`POST` sur la route `deploy/12`.

Extraction des métadonnées
~~~~~~~~~~~~~~~~~~~~~~~~~~

L'intégralité des images Docker utilisées par le MIP sont accessibles en public
sur `Docker Hub <https://hub.docker.com/>`_. Il est donc possible d'accéder aux
métadonnées (LABELS) de leur container par ce site. Cependant, Docker Hub
ne propose pas d'API pour y accéder.
C'est pourquoi l'`API de MicroBadger <https://microbadger.com/api>`_
a été utilisée.
Elle permet de récupérer leurs métadonnées.

Les métadonnées sont définies dans les `LABELS` contenus dans le `Dockerfile`
utilisé pour la contstruction de l'image Docker. Si l'on prend par exemple,
les `LABELS` de l'image Docker `hbpmip/woken`, les labels du Dockerfile
sont les suivants:

.. code-block:: dockerfile

    # Dockerfile

    # ...

    LABEL org.label-schema.schema-version="1.0" \
        org.label-schema.license="Apache 2.0" \
        org.label-schema.name="woken" \
        org.label-schema.description="An orchestration platform for Docker containers running data mining algorithms" \
        org.label-schema.url="https://github.com/LREN-CHUV/woken" \
        org.label-schema.vcs-type="git" \
        org.label-schema.vcs-url="https://github.com/LREN-CHUV/woken" \
        org.label-schema.vendor="LREN CHUV" \
        org.label-schema.version="githash" \
        org.label-schema.docker.dockerfile="Dockerfile" \
        org.label-schema.memory-hint="2048"

Comme Docker n'est pas très contraignant concernant le nom des `LABELS`,
les développeurs du MIP ont choisi d'utiliser `Label Schema <http://label-schema.org/rc1/>`_.
Label Schema est une spécification définissant les conventions de nommage à
respecter pour les métadonnées contenues dans les `LABELS`.
Le nom de chaque `LABEL` faisant partie de la spécification de Label Schema est
préfixé par `org.label-schema`.
`org.label-schema.description` correspond à la description de l'application
contenue dans le container par exemple.

Un service appelé `MicrobadgerService` a été développé pour permettre
de communiquer avec l'API de MicroBadger.
L'implémentation de ce dernier est faite dans le fichier
`maracker/marackerapi/services.py`.

Les métadonnées consommées par le service sont:

- `org.label-schema.description`: Description de l'application.
- `org.label-schema.memory-hint`: Mémoire RAM (en MB) nécessaire pour exécuter
  l'application.

`org.label-schema.cpu-hint` était sensé être utilisé mais il ne faisait plus
partie de la spécification au moment du développement du service.

Pour que ce service fonctionne, il est nécessaire que l'image aie été publiée
sur Docker Hub. Cela se fait facilement il suffit de builder l'image Docker
avec la commande `docker build -t <image-name>:<tag>` dans le dossier contenant
le Dockerfile. Ensuite il faut publier l'imageà l'aide de la commande
`docker push <image-name>:<tag>`.

Ce service fonctionne et permet de récupérer les métadonnées des containers.

Interaction avec l'API Marathon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Comme dit précédemment, Marathon propose une API. Deux routes de cette API
seront utilisées pour lancer le déploiement et la suppression d'une application
sur Marathon.

Les routes de Marathon sont:

- `/apps`: Route permettant de créer et déployer une application.

  - `POST`: Permet de créer une application.

- `/apps/<app-name>`: Permet de modifier/supprimer une application.

  - `DELETE`: Entraîne la suppression de l'application dont le nom est
    celui spécifié par le paramètre `<app-name>`.

Au départ la première idée a été d'utiliser le module Python
`requests <http://docs.python-requests.org/en/master/>`_ mais la bibliothèque
`marathon-python <https://github.com/thefactory/marathon-python>`_
a finalement été utilisée. Utiliser une bibliothèque semblait plus sûr que de
devoir gérer des erreurs venant de l'API de Marathon soi-même.

Cette bibliothèque propose plusieurs classes Python permettant d'interagir avec
Marathon:

- `MarathonClient`: Client permettant de communiquer avec l'API de Marathon.
  Cet objet contient un attribut `url` contenant l'url de l'API de Marathon.
- `MarathonApp`: Objet représentant une application déployable sur Marathon
  (nom, CPU, mémoire, variables d'environnement).
  Cet objet est celui à transmettre au `MarathonClient` pour lancer
  le déploiement.
- `MarathonDockerContainer`: Objet représentant un container Docker
  (image, ports à exposer). Cet objet peut être associé à
  un objet `MarathonApp`.

.. raw:: latex

    \clearpage

Pour le déploiement d'une application à partir d'un objet
`MarathonConfiguration`, le service appelé `MarathonService` est responsable de:

1. Convertir l'objet `MarackerApplication` associé à la `MarathonConfiguration`
   en `MarathonApp`.

2. Définir les différents attributs de l'objet `MarathonApp` créé précédemment
   à partir des informations contenues dans l'objet `MarathonConfiguration`.

3. Si un `DockerContainer` est associé à la `MarackerApplication`, celui-ci
   est converti en `MarathonDockerContainer`. Ce dernier est ensuite associé
   à la `MarathonApp` créée au point 1.

4. Envoyer la requête de déploiement à Marathon en utilisant
   le `MarathonClient` et la `MarathonApp`.

Le déploiement d'une application peut rencontrer plusieurs cas.
Les cas suivants sont gérés:

1. Si le service est installé sur tout le cluster et accessible en ligne de
   commande, la clé `cmd` sera utilisé pour transmettre la commande à utiliser
   pour démarrer le service sur Marathon.

2. Si le service est installé sur tout le cluster et démarrable
   par une commande et que sa configuration (`MarathonConfiguration`)
   contient des arguments, l'attribut `args` de l'objet `MarathonConfiguration` sera
   concaténé avec l'attribut `cmd` de l'objet `MarackerApplication`.
   Le résultat de cette concaténation sera transmis à l'API de Marathon dans
   la clé `cmd`.

3. Si le service est un simple container Docker dont aucun ou plusieurs
   ports doivent être exposés, les informations concernant le container
   seront stockées dans la clé `container` de l'API de Marathon.

4. Si le service est packagé dans un container avec un `ENTRYPOINT` devant
   accepter des arguments, l'attribut `args` de l'objet `MarathonConfiguration`
   doit être défini. La clé `container` de l'API de Marathon contiendra
   les informations relatives au container à exécuter. Les arguments
   à passer au container doivent être définis l'attribut `args` de l'objet
   `MarathonConfiguration` et ils seront transmis à l'API de Marathon en
   utilisant la clé `args`.

5. Si le service est packagé dans un container et doit lancer une commande
   spécifique avec des paramètres, l'attribut `command` de l'object
   `MarackerApplication` doit être défini pour la commande à exécuter.
   L'attribut `args` de l'objet `MarathonConfiguration` doit contenir
   les paramètres qui seront transmis à la commande à lancer dans le container.
   Lors du déploiement sur Marathon, l'attribut `cmd`
   de l'objet `MarackerApplication` et l'attribut `args`
   de l'objet `MarathonConfig` seront concaténés dans la clé `cmd` pour l'API
   de Marahton. La clé `container` contiendra les informations de l'objet
   `DockerContainer`.

Tous les services déployés sur Marathon sont exposés au monde extérieur
grâce à Træfik. Comme dit précédemment, Træfik se base sur les labels
des containers instanciés.
Pour y parvenir, on définit l'attribut `labels` de
l'objet `MarathonApp`. Cet attribut est un dictionnaire dont deux clés
`traefik.frontend.rule` et `traefik.backend` sont définies en se basant
sur le nom de l'application à déployer et l'identifiant de l'objet
`MarathonConfiguration`. Cela permet de limiter le risque de collision
de nom.

Par exemple, si l'application à déployer s'appelle `test` et que l'identifiant
de sa configuration est `12`, `traefik.frontend.rule` prendra la valeur
`Host:test12.marathon.localhost` et `traefik.backend` contiendra `test12`.

Si on reprend l'exemple du service Nginx entré précédemment dans la base de
données, le JSON qui sera envoyé à Marathon sera celui-ci:

.. code-block:: json

  {
    "id": "/nginx-test.4",
    "cmd": null,
    "cpus": 1,
    "mem": 64,
    "instances": 1,
    "container": {
      "type": "DOCKER",
      "docker": {
        "image": "nginx",
        "network": "BRIDGE",
        "portMappings": [
          {
            "containerPort": 80,
            "hostPort": 0
          }
        ],
        "forcePullImage": false
      }
    },
    "labels": {
      "traefik.backend": "nginx-test4",
      "traefik.frontend.rule": "Host:nginx-test4.marathon.localhost"
    }
  }

La clé `portMappings` permet de définir quels ports du container Marathon doit
exposé. `containerPort` correspond au port du container à exposer et `hostPort`
correpond au port qui sera ouvert sur le système hôte. En général, on utilise
la valeur `0` pour laisser Marathon choisir un port libre aléatoirement.
Træfik s'occupera de rendre accessible le port choisi depuis l'extérieur du
réseau.

Les détails d'implémentation du `MarathonService` sont accessibles dans
le fichier `maracker/marackerapi/services.py`.

.. raw:: latex

    \clearpage

Exposition des applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Comme présenté dans le chapitre précédent, l'exposition des applications
fonctionne mais
le mandant aurait voulu que les applications soient regroupées sous le même
domaine et soient accessibles par des préfixes comme `marathon.localhost/app1`
et `marathon.localhost/app2`  au lieu de `app1.marathon.localhost` et
`app2.marathon.localhost`.
Cela n'a pas été fait car certaines applications (typiquement
les applications front-end) ne supportent pas ce type de reverse-proxying.
Cela pose problème en ce qui concerne la racine du domaine qui n'est plus
`marathon.localhost` mais `marathon.localhost/app1/`. La conséquence est
que les fichiers statiques (fichier JavaScript, CSS, images, etc.) ne
sont plus chargés. De ce fait certaines applications ne fonctionnent plus.

Tests
=====

Cette partie décrit les techniques utilisées pour tester l'application.
L'application passe par plusieurs étapes de validation. Une première vise
à vérifier que le code respecte certaines métriques. La seconde consiste
à tester certaines fonctionnalités séparément (tests unitaires).

Comme lancer les tests peut s'avérer long et peut potentiellement être
une tâche que le développeur peut oublier d'exécuter, un outil d'intégration
continue a été utilisé pour automatiser le lancement des tests.

Tests unitaires
~~~~~~~~~~~~~~~

Afin d'éviter des régressions et de garder un code respectant
le `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_, plusieurs outils
ont été utilisés. L'environnement python propose plusieurs logiciels permettant
de garder le code lisible et de le valider.
`YAPF <https://github.com/google/yapf>`_ (Yet Another Python Formatter) permet
de indenter le code de manière à ce qu'il respecte le PEP8.
`flake8 <http://flake8.pycqa.org/en/latest/>`_ permet de vérifier que le code
respecte le PEP8.
Concernant les tests unitaires, Django propose déjà une extension permettant
d'effectuer des tests. Il suffit de définir un test case, une méthode
:code:`setUp` qui permet d'instancier par exemple un client pour tester
une API. Il suffit ensuite de définir des méthodes suivant le pattern
:code:`test_what_you_test` implémentant chacune un test unitaire.
Il est ensuite possible d'utiliser des assertions afin de valider
les résultats.

Voici un exemple définissant un cas de test avec deux tests unitaires:

.. code-block:: python

    from django.test import TestCase
    from .services import MicrobadgerService


    class MicrobadgerTestCase(TestCase):
        def setUp(self):
            pass

        def test_service_can_fetch_data_and_create_model(self):
            microbadger_data = MicrobadgerService.get_docker_metadata(
                'hbpmip', 'portal-backend')
            self.assertIsNotNone(microbadger_data)

        def test_service_handle_non_existent_image(self):
            microbadger_data = MicrobadgerService.get_docker_metadata(
                'toto', 'portal-backend')
            self.assertIsNone(microbadger_data)

Le développeur est supposé lancer tous les tests suivants afin de valider
son code et de vérifier qu'il n'y a aucune régression:

1. Utiliser YAPF et flake8 sur tous les scripts python *qui n'ont pas été générés
   automatiquement*.
2. Lancer les tests unitaires de Django pour déceler les éventuelles régressions.

Si tous les tests passent, le développeur peut commiter et pusher
ses modifications sur le dépôt. La qualité du code reste acceptable tant que
le développeur effectue ces vérifications avant chaque commit.
Le problème est que ce genre de tâches sont facilement oubliées et ne sont pas
réalisées avant chaque commit. C'est là que vient l'intérêt d'utiliser
un outil d'intégration continue (*CI*) comme
`Travis CI <https://travis-ci.org/>`_. Cet outil sera présenté plus tard dans
ce document.

Les tests suivants ont été réalisés pour tester le fonctionnement de l'API:

- Service `MicrobadgerService`:

  - Récupération des métadonnées d'une image Docker existante.

  - Tentative de recherche pour une image Docker qui n'existe pas.

- Service `MarathonService`:

  - Déploiement d'une application puis suppression de cette application.

- Tests de l'API

  - Création d'une application sans container.

  - Création d'une application utilisant un container.

  - Création d'une application avec ses configurations Marathon.

  - Mise à jour d'une application (écrasement des configurations Marathon
    avec de nouvelles configurations).

Les détails de tous ces tests sont dans le fichier
`maracker/marackerapi/tests.py`.

Travis CI: un outil d'intégration continue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ce type d'outils permet de monitorer le dépôt Git d'un projet et de réaliser
des actions à chaque nouveau push. De cette manière, on peut facilement
lancer les tests à chaque push et ainsi éliminer la probabilité que le projet
soit «cassé» sans que le développeur s'en rende compte rapidement.
En général, les outils de CI (Continuous Integration)
donnent accès aux logs de chaque build/batterie de test et
notifient le développeur par email si une erreur est survenue.

Travis a été choisi parce qu'il est prévu pour exécuter des tests unitaires et
supporte de nombreux langages (Python, Ruby, C, PHP, Java, etc.). À cela
s'ajoute le fait que cet outil est facile à configurer.
Il suffit de réaliser les actions suivantes pour utiliser Travis CI pour
son projet:

1. Se connecter à `https://travis-ci.org/ <https://travis-ci.org/>`_ avec
   son compte GitHub.
2. Ajouter le dépôt GitHub aux dépôts que Travis doit surveiller.
3. Créer un fichier :code:`.travis.yml` et l'ajouter dans le dépôt. Ce fichier
   décrit la configuration de Travis; langage, OS,
   installation des dépendances, scripts de tests, etc.

Si la configuration est bien faite, Travis devrait builder à chaque push sur
le dépôt. Pour tester, il suffit de modifier un fichier du dépôt puis
de commiter et pusher ses modifications sur le dépôt. Si le build passe ou
échoue, un email de notification est envoyé aux développeurs. Il est également
possible de vérifier l'état du dernier build ainsi que l'historique des builds
sur le site de Travis.

Voici un exemple de fichier de configuration pour Travis CI:

.. code-block:: yaml

    language: python
    python:
      - "3.6"
    install:
      - pip install flake8
      - pip install -r requirements.txt
    before_script:
      - flake8 maracker
    script:
    - python maracker/manage.py test

Ici on spécifie que le langage du projet est :code:`Python` et que la version
de Python à utiliser est :code:`python 3.6`. On définit ensuite comment
les dépendances doivent être installées (ici avec :code:`pip install`).
Une fois les dépendances installées, on entre dans la partie avant les tests
qui consiste à vérifier que le code respecte le PEP8.
Finalement, on lance les tests avec le fichier :code:`manage.py` de Django.

La mise en place des tests a permis de faciliter le refactoring des modèles
et le débuggage de l'API.

Difficultés et problèmes rencontrés
===================================

Même si la communication n'a pas été simple au début du projet et que
la définition des objectifs a pris beaucoup de temps, une ligne
directrice plus claire a pu être donnée lors de la deuxième phase du projet.

Le nombre de technologies à prendre en main n'a pas favorisé la compréhension
de la problématique mais en tester une partie a permis de mieux comprendre
les besoins du mandant. Les connaissances de l'équipe de développeurs du CHUV
ont également pu aider le développeur lorsqu'il avait des questions.

Résultats obtenus
=================

Les outils ZooKeeper, Mesos (primary et replica), Marathon, Træfik ont été mis
en place et l'API Maracker remplit une partie des fonctionnalités
décrites dans le cahier de charges.

Il est possible de tester l'ensemble de l'infrastructure. Pour cela, il faut
disposer d'un système GNU/Linux avec les logiciels `git`, `Docker` et
`Docker Compose` installés.
Il suffit ensuite de cloner le dépôt avec
`git clone https://github.com/groovytron/maracker.git`, se placer dans
le dossier `maracker` téléchargé et lancer le script `run.sh`.

Une fois le script exécuté, les différents services sont accessibles aux
adresses suivantes:

- marathon.localhost: Marathon

- chronos.localhost: Chronos

- traefik.localhost: Træfik

- localhost:8000: API Maracker

Il est ensuite possible de tester l'API en essayant d'ajouter un service.
Voici un exemple utilisant déployant un service nginx. Ce service a été
choisi parce que son container par défaut affiche une page d'index et
qu'une application de démonstration plus élaborée n'a pas pu être développée
faute de temps.

Voici le fichier JSON envoyé à l'API pour ajouter le service Nginx:

.. literalinclude:: examples/maracker/docker-nginx.json
   :language: json

Si on désire arrêter l'infrastructure, il suffit de lancer la commande
`docker-compose stop`.

Les figures suivantes montrent une partie de ce qui a été développé.
Ici, l'infrastructure est démarrée puis un service est ajouté à la base
de données avant de le déployer.

.. figure:: images/demo/run-script.png
   :align: center
   :alt: Lancement du script de démarrage de l'infrastructure

   Lancement du script de démarrage de l'infrastructure

.. figure:: images/demo/marathon-ui.png
   :align: center
   :alt: Interface web de Marathon (aucune application)

   Interface web de Marathon (aucune application)

.. figure:: images/demo/traefik-ui.png
   :align: center
   :alt: Interface web de Træfik (Marathon, Chronos et Træefik)

   Interface web de Træfik (Marathon, Chronos et Træefik)


.. figure:: images/demo/create-nginx.png
   :align: center
   :alt: Création du service en utilisant l'API

   Création du service en utilisant l'API

.. figure:: images/demo/list-apps.png
   :align: center
   :alt: Liste des services disponibles

   Liste des services disponibles

.. figure:: images/demo/deploy-nginx.png
   :align: center
   :alt: Déploiement du service

   Déploiement du service

.. figure:: images/demo/marathon-nginx.png
   :align: center
   :alt: Nginx déployé sur Marathon

   Nginx déployé sur Marathon

.. figure:: images/demo/traefik-nginx.png
   :align: center
   :alt: Nginx détecté et exposé par Træfik

   Nginx détecté et exposé par Træfik

.. figure:: images/demo/nginx-url.png
   :align: center
   :alt: Accès à Nginx par son nom de domaine

   Accès à Nginx par son nom de domaine

Conclusion
==========

Si l'on reprend les objectifs initiaux, la base de données et l'API
ont été mises en place.
Elles suffisent pour gérer des services simples mais ne supportent pas
Boutiques. Cela peut consister en une amélioration future mais cela
demanderait d'y ajouter également le support de Chronos.
Supporter l'ajout de Workflows décrits dans le format de Boutiques
dans la base de données ainsi que les exécuter sur Chronos constituerait
une amélioration future intéressante.

Il est possible d'effectuer du CRUD sur les différents modèles (application,
container Docker et configuration Marathon) et de demander le déploiement
de l'application sur Marathon.

Concernant l'exposition des services à leur démarrage, Træefik a été mis
en place pour remplir ce rôle et l'API s'occupe elle-même d'ajouter les labels
nécessaires pour que Træfik expose ces applications.

Seul le frontend n'a pas pu être développé. Comme cette fonctionnalité pourrait
faciliter l'utilisation de l'API pour un utilisateur, cela constitue une tâche
prioritaire dans les améliorations futures.

Une autre amélioration possible serait de trouver une solution pour exposer
toutes les applications déployées sous un même nom de domaine et garantir
que leur fonctionnement (notammnent le chargement des fichiers statiques)
ne sera pas entravé.

Remerciements
=============

Je tiens à remercier Yoan Blanc (:code:`@greut`) pour son assistance technique
concernant la mise en place de l'infrastructure et les réflexions sur
l'utilisaton des outils et la relecture du rapport.

Je tiens également à remercier Aïcha Rizzotti pour l'encadrement de ce projet.

Je remercie aussi Ludovic Claude pour ses conseils techniques et l'aide qu'il
a fournis pour m'assister dans la compréhension du fonctionnement de
l'infrastructure du MIP.

.. bibliography:: references.bib
   :notcited:
   :style: unsrt
