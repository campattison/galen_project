# Translation Evaluation: On Mixtures

**Generated:** 2026-01-22 09:20

This document provides a side-by-side comparison of translations and their evaluation scores for validation and transparency.

## Summary

### Overall Rankings

| Rank | Model | Score |
|------|-------|-------|
| 🥇 1 | GEMINI | 0.6156 |
| 🥈 2 | CLAUDE | 0.6078 |
| 🥉 3 | OPENAI | 0.5886 |

### Methodology

- **BLEU-4, chrF++, METEOR**: Multi-reference (n-grams matched against ANY reference)
- **ROUGE-L, BERTScore, COMET**: Max score across references

---

## Chunk-by-Chunk Analysis

### Chunk 1

#### Source (Greek)

> Ὅτι μὲν ἐκ θερμοῦ καὶ ψυχροῦ καὶ ξηροῦ καὶ ὑγροῦ τὰ τῶν ζῴων σώματα κέκραται καὶ ὡς οὐκ ἴση πάντων ἐστὶν ἐν τῇ κράσει μοῖρα, παλαιοῖς ἀνδράσιν ἱκανῶς ἀποδέδεικται φιλοσόφων τε καὶ ἰατρῶν τοῖς ἀρίστοις· εἴρηται δὲ καὶ πρὸς ἡμῶν ὑπὲρ αὐτῶν τὰ εἰκότα δι’ ἑτέρου γράμματος, ἐν ᾦ περὶ τῶν καθ’ Ἱπποκράτην στοιχείων ἐσκοπούμεθα. νυνὶ δ’, ὅπερ ἐστὶν ἐφεξῆς ἐκείνῳ, ἁπάσας ἐξευρεῖν τῶν κράσεων τὰς διαφοράς, ὁπόσαι τ’ εἰσὶ καὶ ὁποῖαι κατ’ εἴδη τε καὶ γένη διαιρουμένοις, ἐν τῷδε τῷ γράμματι δίειμι τὴν ἀρχὴν ἀπὸ τῆς τῶν ὀνομάτων ἐξηγήσεως ποιησάμενος. ἐπειδὰν μὲν γὰρ ἐκ θερμοῦ καὶ ψυχροῦ καὶ ξηροῦ καὶ ὑγροῦ κεκρᾶσθαι λέγωσι τὰ σώματα, τῶν ἄκρως τοιούτων ἀκούειν φασὶ χρῆναι, τουτέστι τῶν στοιχείων αὐτῶν, ἀέρος καὶ πυρὸς καὶ ὕδατος καὶ γῆς· ἐπειδὰν δὲ ζῷον ἢ φυτὸν ἤτοι θερμὸν ἢ ψυχρὸν ἢ ξηρὸν ἢ ὑγρὸν εἶνα...

#### Reference Translations

**Reference 1:**
> That the bodies of animals are compounded from hot, cold, dry, and wet, and that all the parts are not equal in their krasis, has been adequately shown by the ancients—the best of both philosophers and doctors. The probabilities regarding these were also stated by us in another work, in which we examined the elements according to Hippocrates. What follows now in sequence, which is next in order to that, is to discover all the differentiae of the krasias. In this work, I shall go through how many there are and of what kinds, divided according to class and kind, making a start from the explanati...

**Reference 2:**
> That the bodies of animals consist of a mixture of hot, cold, dry and wet and that there is not an equal portion of all these in the mixture, has been adequately demonstrated by men of ancient times, the best of both philosophers and doctors; and the appropriate things have been stated by us, too, in a separate work, in which we investigated the elements according to Hippocrates. Now, however, I shall do what follows on from that, namely go through in this work the discovery of all the distinct types of mixtures: how many there are, and of what kind, as one separates them by genus and species;...

#### Model Translations & Scores

**CLAUDE**

> That the bodies of animals are compounded from hot and cold and dry and moist, and that the share of each in the mixture is not equal in all cases, has been sufficiently demonstrated by the ancients, by the best of both philosophers and physicians. We too have stated what is reasonable concerning these matters in another work, in which we examined the elements according to Hippocrates. But now, which is the next step after that work, I shall proceed in this present treatise to discover all the differences of mixtures, both how many they are and of what sort when divided according to species an...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.4572 |
| chrF++ | 0.5843 |
| METEOR | 0.5579 |
| ROUGE-L | 0.6134 |
| BERTScore | 0.9285 |
| COMET | 0.8256 |

**GEMINI**

> That the bodies of living beings are mixed from the hot and the cold and the dry and the wet, and that the portion of all of these in the mixture is not equal, has been sufficiently demonstrated by ancient men, by the best of both philosophers and physicians; and what is fitting concerning them has also been stated by us in another treatise, in which we examined the elements according to Hippocrates. But now, in this treatise, I shall proceed to the topic that follows upon that one, namely, to discover all the differences of the mixtures—how many and of what sort they are, when divided accordi...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.4106 |
| chrF++ | 0.5908 |
| METEOR | 0.5345 |
| ROUGE-L | 0.6007 |
| BERTScore | 0.9338 |
| COMET | 0.8315 |

**OPENAI**

> That the bodies of animals are composed by mixture from the hot, the cold, the dry, and the moist, and that the share of each in the mixture is not equal, has been sufficiently demonstrated by men of old, both by philosophers and by the best physicians; and I too have set forth the probable considerations concerning these matters in another treatise, in which we examined the elements according to Hippocrates. Now, as what follows upon that, I shall in this work investigate all the differences of temperaments—how many they are and of what sort, when distinguished by species and by genera—beginn...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3952 |
| chrF++ | 0.5741 |
| METEOR | 0.5000 |
| ROUGE-L | 0.5775 |
| BERTScore | 0.9274 |
| COMET | 0.8235 |

---

### Chunk 2

#### Source (Greek)

> καὶ τοῦτό γ’ ἐστὶ τὸ μάλιστα νοσῶδες ἐργαζόμενον τὸ φθινόπωρον, ἡ ἀνωμαλία τῆς κράσεως. οὐκ ὀρθῶς οὖν εἴρηται ψυχρὸν καὶ ξηρόν, οὐ γάρ ἐστι ψυχρόν αὐτὸ καθ’ αὑτὸ θεωρούμενον, ὥσπερ ὁ χειμών, ἀλλὰ τῷ θέρει παραβαλλόμενον ἐκείνου ψυχρότερον. οὐ μὴν οὐδ’ ὁμαλῶς εὔκρατον, ὡς τὸ ἔαρ, ἀλλ’ ἐν τούτῳ δὴ καὶ μάλιστα διενήνοχεν ἐκείνης τῆς ὥρας, ὅτι τὴν εὐκρασίαν τε καὶ τὴν ὁμαλότητα διὰ παντὸς ἴσην οὐ κέκτηται. πολὺ γὰρ θερμότερόν ἐστι κατὰ τὴν μεσημβρίαν ἢ κατὰ τὴν ἕω τε καὶ τὴν ἑσπέραν. ὑγρότητος δὲ καὶ ξηρότητος οὐκ ἀκριβῶς μέν ἐστι μέσον, ὡς τὸ ἔαρ, ἀλλ’ ἐπὶ τὸ ξηρότερον ῥέπει. λείπεται δὲ κἀν τούτῳ τοῦ θέρους, οὐ μὴν τοσοῦτόν γ’ ὅσον θερμότητι. δῆλον οὖν, ὡς οὐδὲ τὸ φθινόπωρον ἁπλῶς οὕτω ῥητέον, ὡς ἐκεῖνοι λέγουσι, ψυχρόν τ’ εἶναι καὶ ξηρόν. ἄκρως μὲν γὰρ οὐδέτερόν ἐστιν, ἐπικρατεῖ δ’ ἐν αὐτῷ ...

#### Reference Translations

**Reference 1:**
> And this, the non-uniformity of the krasis, is what makes the autumn particularly baneful. Therefore, it is not correctly described as cold and dry, for it is not to be considered cold in itself, like the winter, but when compared to summer it is colder than that. Nor again is it uniformly eukratic, like the spring, but in this differs most from that season because it has not acquired the equal eukrasia and evenness throughout. For autumn is much hotter at midday than it is at dawn or dusk, and it is not precisely midway between wetness and dryness as spring is, but tends toward being drier. H...

#### Model Translations & Scores

**CLAUDE**

> And this is what most produces the diseased condition of autumn, the irregularity of its mixture. Therefore it has not been correctly stated that it is cold and dry, for it is not cold when considered in itself, as winter is, but only colder than summer when compared to it. Nor indeed is it uniformly well-tempered, as spring is, but in this very respect it differs most from that season, because it does not possess an equal temperament and uniformity throughout. For it is much hotter at midday than at dawn and evening. As regards moisture and dryness, it is not precisely intermediate, as spring...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3606 |
| chrF++ | 0.5645 |
| METEOR | 0.5072 |
| ROUGE-L | 0.5302 |
| BERTScore | 0.9191 |
| COMET | 0.8298 |

**GEMINI**

> And this is indeed what makes autumn most productive of disease: the irregularity of its temperament. Therefore, it has been incorrectly stated that it is cold and dry. For it is not cold when considered in and of itself, as winter is, but when compared with summer, it is colder than it. Moreover, it is not evenly well-tempered, as spring is, but it is in this very point that it differs most from that season, in that it does not possess a good temperament and evenness that are constant throughout. For it is much hotter at midday than at dawn and evening. And with respect to wetness and dryness...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3249 |
| chrF++ | 0.5744 |
| METEOR | 0.5006 |
| ROUGE-L | 0.5195 |
| BERTScore | 0.9099 |
| COMET | 0.8324 |

**OPENAI**

> And this, indeed, is what makes autumn especially disease-producing: the irregularity of its temperament. It has not, then, been rightly called cold and dry, for it is not cold when considered in itself, as winter is, but only in comparison with summer is it the colder. Nor is it uniformly temperate, as spring is; rather, it differs above all from that season in this, that it does not maintain temperateness and uniformity equally throughout. For it is much warmer at midday than in the morning and evening. And as regards moisture and dryness, it is not exactly at the mean, as spring is, but inc...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3444 |
| chrF++ | 0.5380 |
| METEOR | 0.4810 |
| ROUGE-L | 0.4667 |
| BERTScore | 0.9095 |
| COMET | 0.8284 |

---

### Chunk 3

#### Source (Greek)

> ἐν τούτοις δὲ τὸ μὲν πρὸς ἄνθρωπον παραβάλλειν πρὸς ὁμοειδές ἐστι παραβάλλειν, τὸ δὲ πρὸς μέλιτταν ἢ μύρμηκα πρὸς ὁμογενές, ὡσαύτως δὲ καὶ πρὸς φυτὸν ὁτιοῦν. ἔστι γὰρ ἀνωτέρω τοῦ ζῴου τοῦτο τὸ γένος, ὥσπερ οὖν καὶ αὐτοῦ τούτου λίθος καὶ σίδηρος καὶ χαλκὸς ἐκ τῶν ἄνωθεν γενῶν. καλείσθω γοῦν 〈πρὸς〉 ὁμογενὲς ἕνεκα συντόμου διδασκαλίας ἡ τοιαύτη σύμπασα παραβολή, τοσόνδε μόνον ἐν αὐτῇ διελομένων ἡμῶν, ὡς, ἐπειδὰν μὲν ἁπλῶς οὐσία τις εὔκρατος λέγηται καὶ ταύτης δέ τις ἑτέρα ξηροτέρα καὶ θερμοτέρα καὶ ψυχροτέρα καὶ ὑγροτέρα, τὴν μὲν εὔκρατον ἐνταῦθα τὴν ἐκ τῶν ἐναντίων ἀκριβῶς ἴσων συνελθόντων ὀνομάζομεν, ὅσον δ’ ἀπολείπεται τῆσδε καὶ πλεονεκτεῖ κατά τι, τῷ τοῦ πλεονεκτοῦντος ὀνόματι προσαγορεύομεν· ἐπειδὰν δ’ ἤτοι φυτὸν εὔκρατον ἢ ζῷον ὁτιοῦν εἴπωμεν, οὐκέθ’ ἁπλῶς ἀλλήλοις ἐν τῇ τοιαύτῃ λέξει τ...

#### Reference Translations

**Reference 1:**
> In these, the comparison to a human is a comparison to the same kind (species), while that to a bee or ant is to the same class, and similarly also to a plant of whatever kind. For this class is higher than that of animal just as also that of stone, iron, and copper is from the classes higher than this itself. Anyway, for the sake of brevity in teaching, let every such comparison be called homogenous, while we make a distinction in this only as much as when some substance is called eukratic in an absolute sense, while some other substance is drier, hotter, colder, and wetter than this, we term...

**Reference 2:**
> Of these, the comparison with another man is a comparison within the same species, while the comparison with bees or ants is one within the same genus, as, equally, is the comparison with any plant. The genus in question in the latter case is a higher one than that of animals; so, in the same way, that which includes stone, iron and bronze is even higher than that. So, for the sake of brevity of exposition, let all comparisons of this kind be called comparisons within the same genus. But let us just make this distinction among them: that when some existent object is called well-mixed in absolu...

#### Model Translations & Scores

**CLAUDE**

> In these cases, comparison with a human being is comparison with something of the same species, while comparison with a bee or an ant is comparison with something of the same genus, and likewise also with any plant whatsoever. For this genus is higher than the animal, just as stone and iron and bronze are from genera still higher than this. Let such comparison in its entirety be called comparison with something of the same genus, for the sake of concise instruction, our only distinction in this matter being as follows: whenever some substance is said to be well-tempered in an absolute sense, a...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2442 |
| chrF++ | 0.5261 |
| METEOR | 0.4754 |
| ROUGE-L | 0.4991 |
| BERTScore | 0.9080 |
| COMET | 0.7921 |

**GEMINI**

> Among these, however, comparing to a human being is a comparison to something of the same species, whereas comparing to a bee or an ant is a comparison to something of the same genus, and likewise also to any plant whatsoever. For this genus is higher than that of ‘animal’, just as, in turn, stone and iron and bronze belong to the genera above this one. Let this entire sort of comparison, at any rate, be called a comparison to something of the same genus for the sake of concise instruction, provided that we make only the following distinction within it: namely that, on the one hand, whenever s...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3009 |
| chrF++ | 0.5550 |
| METEOR | 0.5242 |
| ROUGE-L | 0.5052 |
| BERTScore | 0.9030 |
| COMET | 0.8117 |

**OPENAI**

> In these cases, to compare with a human being is to compare with something of the same species, whereas to compare with a bee or an ant is to compare with something of the same genus—and likewise with any plant whatever. For this genus stands higher than “animal,” just as, moreover, stone, iron, and bronze too derive from the genera higher up. Let, then, for the sake of concise instruction, the whole of such comparison be called comparison to what is of the same genus, with only this distinction drawn within it by us: whenever a simple substance is called well-tempered, and another of the same...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2421 |
| chrF++ | 0.5201 |
| METEOR | 0.4762 |
| ROUGE-L | 0.4557 |
| BERTScore | 0.9031 |
| COMET | 0.8071 |

---

### Chunk 4

#### Source (Greek)

> ὅσα μὲν οὖν σκληρότερα τοῦ δέρματός ἐστι μόρια, καθάπερ ὀστᾶ καὶ χόνδροι καὶ κέρατα καὶ τρίχες ὄνυχές τε καὶ σύνδεσμοι καὶ ὁπλαὶ καὶ πλῆκτρα, πλέον ἐν τούτοις ἐστὶ τὸ ξηρόν· ὅσα δὲ μαλακώτερα, καθάπερ αἷμα καὶ φλέγμα καὶ πιμελὴ καὶ στέαρ καὶ μυελὸς ἐγκέφαλός τε καὶ νωτιαῖος, ὑγροῦ πλέον ἐν τούτοις ἐστὶν ἢ ξηροῦ· καὶ μὲν δὴ καὶ ὅσῳ τὸ πάντων ξηρότατον ἐν ἀνθρώπῳ μόριον ὑπερβάλλει σκληρότητι τοῦ δέρματος, τοσούτῳ πάλιν ἀπολείπεται τὸ ὑγρότατον. ἔοικε δέ πως ὁ λόγος ἤδη τῶν χρησιμωτάτων αὐτῶν ἐφάπτεσθαι καὶ διδάσκειν, ἅμα μὲν ὡς οὐ ζῴων μόνον, ἀλλὰ καὶ τῶν ἄλλων ἁπάντων σωμάτων εὐκρατότατός ἐστιν ὁ ἄνθρωπος, ἅμα δ’ ὡς τῶν ἐν αὐτῷ μορίων τὸ τῆς χειρὸς δέρμα τὸ ἔσωθεν ἁπάσας ἐκπέφευγεν ἀκριβῶς τὰς ὑπερβολάς. Ἐπιστήσαντες οὖν πάλιν ἐνταῦθα τὸν λόγον ἐπισκεψώμεθα, τίς ἄριστα κέκραται πάντων ἄνθρω...

#### Reference Translations

**Reference 1:**
> Therefore, those parts that are harder than skin, such as bones, cartilages, horns, hair, nails, ligaments, hooves, and spurs have more dry in them, whereas those that are softer, like blood, phlegm, soft fat, hard fat, marrow, brain, and spinal cord, have more wet in them than dry. Furthermore, the amount by which the driest part of all in a human exceeds the dryness of the skin is in turn that by which the wettest part is deficient. The argument already seems somehow to touch on what is most useful, and to teach that the human is at the same time not only the most eukratic of animals and of ...

#### Model Translations & Scores

**CLAUDE**

> All those parts, then, which are harder than the skin, such as bones and cartilages and horns and hairs and nails and ligaments and hooves and spurs, contain more of the dry element; but all those which are softer, such as blood and phlegm and fat and suet and marrow and brain and spinal cord, contain more of the moist than the dry. And indeed, by as much as the driest part of all in man exceeds the skin in hardness, by so much in turn does the moistest fall short of it. The discussion seems now somehow to be touching upon the most useful matters and to be teaching, on the one hand, that man i...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3190 |
| chrF++ | 0.5080 |
| METEOR | 0.4512 |
| ROUGE-L | 0.5096 |
| BERTScore | 0.9024 |
| COMET | 0.7722 |

**GEMINI**

> Now then, in as many parts as are harder than the skin, such as bones and cartilages and horns and hairs and nails and ligaments and hooves and spurs, there is more of the dry in them; but in as many as are softer, such as blood and phlegm and soft fat and hard fat and marrow, both cerebral and spinal, there is more of the moist in them than of the dry; and indeed, by as much as the driest part of all in a human being exceeds the skin in hardness, by so much in turn does the moistest part fall short of it. But the argument seems in a way already to be touching upon the most useful points thems...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3203 |
| chrF++ | 0.5416 |
| METEOR | 0.4629 |
| ROUGE-L | 0.5545 |
| BERTScore | 0.9088 |
| COMET | 0.7877 |

**OPENAI**

> Accordingly, whatever parts are harder than the skin—bones, cartilages, horns, hairs, nails, ligaments, hoofs, and spurs—the dry element predominates in these; whereas those that are softer—blood, phlegm, adipose tissue, tallow, and marrow, both cerebral and spinal—have more of the moist than of the dry. And indeed, by just so much as the driest part in a human being exceeds the skin in hardness, by just so much, conversely, does the moistest fall short of it. The argument already seems in some way to be touching upon and teaching their most useful aspects—both that the human being is the most...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2953 |
| chrF++ | 0.5275 |
| METEOR | 0.4170 |
| ROUGE-L | 0.4725 |
| BERTScore | 0.8960 |
| COMET | 0.7882 |

---

### Chunk 5

#### Source (Greek)

> Αὖθις δ’ ἀπὸ τῶν ἐνεργειῶν οἱ μὲν ὅτι καὶ αὐξάνονται καὶ πλειόνων ἢ κατὰ τὴν ἀναλογίαν τοῦ σώματος ὀρέγονταί τε καὶ κρατοῦσιν ἐδεσμάτων, ἰσχυρὰν ἐν τοῖς παισὶν εἶναί φασι τὴν θερμασίαν· οἱ δὲ τὸ μὲν αὐξάνεσθαι διὰ τὴν ὑγρότητα μᾶλλον ἢ τὴν τοῦ θερμοῦ ῥώμην ὑπάρχειν αὐτοῖς φασι, ταῖς μέντοι πέψεσιν οὐχ ὅπως πλεονεκτεῖν ἀλλὰ καὶ πολὺ τῶν ἀκμαζόντων ἀπολείπεσθαι. ἐμέτους τε γὰρ ἀπέπτων αὐτοῖς γίγνεσθαι σιτίων καὶ διαχωρήσεις ὑγρῶν καὶ τραχέων καὶ ἀχυμώτων. εἰ δ’ ὀρέγονται πλειόνων, οὐδὲν εἶναι τοῦτό φασι πρὸς τὴν ῥώμην τοῦ θερμοῦ. πρῶτον μὲν γὰρ οὐδὲ πλεονεξίᾳ θερμότητος ὀρέγεσθαι τὰ ζῷα, τοὐναντίον [δ’] ἅπαν ἀποψυχομένων τῶν ὀρεκτικῶν μορίων· ἔπειτα δὲ διότι μὴ μόνον εἰς θρέψιν ἀλλὰ καὶ εἰς αὔξησιν αὐτοῖς ἡ τροφὴ διοικεῖται, διὰ τοῦτο πλειόνων ἐδεσμάτων προσδεῖσθαι. κατὰ μέντοι τὰς ἄλλας ἁπά...

#### Reference Translations

**Reference 1:**
> In turn, from the functions, there are those who say the heat is strong in children because they grow and desire and have power over more foods than are in proportion to the body, while there are those who say growth is due more to the wetness than to the strength of the heat in them, and that not only do they not predominate in the concoctions in this matter, but also they are consistently lacking compared to those in their prime. For vomits of unconcocted foods occur in them as do excretions, since the foods themselves are watery, rough, and have not as yet been changed in flavor. If, howeve...

**Reference 2:**
> Again, on the basis of the activities, too, the former group claim that because children grow and have a greater appetite and greater capacity to dominate food than is proportionate with the size of their bodies, the heat is strong in children; the latter, that their growth is due to wetness rather than to the strength of the hot, and that their coction, so far from being superior to that of those in their prime, is actually far inferior. For, as they point out, children frequently vomit undigested food, as well as excreting fluids that are both rough and lacking in moisture. As for their grea...

#### Model Translations & Scores

**CLAUDE**

> Again, from their activities, some say that the heat in children is strong because they both grow and desire and consume foods in greater quantity than is proportionate to their body. But others say that their growth occurs rather through moisture than through the strength of heat, and that in digestions they not only do not have an advantage but actually fall far short of those in their prime. For they say that vomiting of undigested foods occurs in them, as well as discharges that are fluid, rough, and lacking in proper humor. And if they desire more food, they say this has nothing to do wit...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3219 |
| chrF++ | 0.5370 |
| METEOR | 0.4309 |
| ROUGE-L | 0.5331 |
| BERTScore | 0.9106 |
| COMET | 0.7735 |

**GEMINI**

> Again, based on their functions, some say that the heat in children is strong, because they both grow and desire and consume more foods than is in proportion to their body; others, however, say that their growing is due to their moisture rather than the strength of their heat, and that with respect to their digestions, they not only have no advantage but even fall far short of those in their prime. For vomits of undigested foods occur in them, as well as evacuations that are liquid, harsh, and lacking in good chyme. And if they desire more food, they say this has no bearing on the strength of ...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3225 |
| chrF++ | 0.5502 |
| METEOR | 0.4540 |
| ROUGE-L | 0.5404 |
| BERTScore | 0.9112 |
| COMET | 0.7760 |

**OPENAI**

> Again, from the standpoint of their functions, some say that, because children both grow and desire and can handle more food than is proportionate to their body, the heat in them is strong; others maintain that their growth is due rather to moisture than to the strength of heat, and that in digestion they not only do not have the advantage but fall far short of those in their prime. For undigested vomitings of food occur in them, and discharges of thin, rough, and sapless matter. And if they crave more, this, they say, is no indication of the vigor of the heat. For, in the first place, animals...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2459 |
| chrF++ | 0.4968 |
| METEOR | 0.3654 |
| ROUGE-L | 0.4796 |
| BERTScore | 0.9005 |
| COMET | 0.7653 |

---

### Chunk 6

#### Source (Greek)

> πάντες δ’ ὑμένες ἤδη ξηρότεροι δέρματος, ὥσπερ γε καὶ αἱ περὶ τὸν ἐγκέφαλόν τε καὶ τὸν νωτιαῖον μήνιγγες· ὑμένες γὰρ δὴ καὶ αἵδε. καὶ μὲν δὴ καὶ σύνδεσμοι πάντες, εἰς ὅσον σκληρότεροι δέρματος, εἰς τοσοῦτον καὶ ξηρότεροι. καὶ οἱ τένοντες δέ, κἂν εἰ τῶν συνδέσμων εἰσὶ μαλακώτεροι, δέρματος γοῦν ἐναργῶς ἤδη σκληρότεροι. χόνδροι δὲ μετὰ τοὺς συνδέσμους εἰσὶ καὶ τι μέσον ἀμφοῖν σῶμα· καλοῦσι δ’ αὐτὸ νευροχονδρώδη σύνδεσμον ἔνιοι τῶν ἀνατομικῶν. ἔστι δὲ τοῦτο σύνδεσμος σκληρὸς καὶ χονδρώδης. ὀστοῦν δὲ τὸ πάντων σκληρότατον, ὧν καλύπτει τὸ δέρμα, καὶ τῶν ἐξεχόντων αὐτοῦ ξηρότατον μὲν ἡ θρίξ, ἐφεξῆς δὲ κέρας, εἶτ’ ὄνυχές τε καὶ ὁπλαὶ καὶ πλῆκτρα καὶ ῥάμφη καὶ ὅσα τοιαῦτα καθ’ ἕκαστον τῶν ἀλόγων ζῴων ἐστὶ μόρια. Τῶν δὲ χυμῶν ὁ μὲν χρηστότατός τε καὶ οἰκειότατός ἐστι τὸ αἷμα. τούτου δ’ οἷον ὑπόστασ...

#### Reference Translations

**Reference 1:**
> All membranes are already drier than skin, just as in fact the meninges around the brain and spinal cord also are, for these are certainly membranes. And furthermore, all ligaments are drier to the degree they are harder than skin, while the tendons, even though they are softer than the ligaments, are in fact already clearly harder than skin. Cartilages are after the ligaments, and there is a body midway between both, which some anatomists call “neurocartilaginous ligament.” This is a hard and cartilaginous ligament. Bone, however, is the hardest of all those [structures] the skin conceals. Of...

**Reference 2:**
> All membranes, certainly, are drier than skin, as are the meninges in the region of the brain and the spinal cord; for these are membranes too. All ligaments, too, are drier than skin, to the same degree that they are harder. The tendons, though softer than the ligaments, are manifestly harder than the skin. Cartilage comes after ligament; and there is a kind of body which is midway between the two, and is referred to by some anatomical writers as ‘nerve-gristly ligament’. This is a hard, gristly kind of ligament. Bone is the hardest of all things hidden beneath the skin; of those that protrud...

#### Model Translations & Scores

**CLAUDE**

> All membranes are already drier than skin, just as indeed are the meninges around both the brain and the spinal cord; for these too are membranes. And furthermore all ligaments, to the extent that they are harder than skin, to that extent are they also drier. And tendons too, even if they are softer than ligaments, are at any rate manifestly harder than skin. Cartilages come after ligaments and are a body intermediate between both; some anatomists call this a neuro-cartilaginous ligament. This is a hard and cartilaginous ligament. Bone is the hardest of all things that skin covers, and of its ...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.4279 |
| chrF++ | 0.6244 |
| METEOR | 0.4886 |
| ROUGE-L | 0.6745 |
| BERTScore | 0.9327 |
| COMET | 0.7974 |

**GEMINI**

> And all membranes are in fact drier than skin, just as are the meninges around the brain and the spinal marrow; for these too are indeed membranes. And indeed, all ligaments, to the extent that they are harder than skin, are to that extent also drier. And the tendons, too, even if they are softer than the ligaments, are at any rate now clearly harder than skin. And cartilages are after the ligaments, and are a certain body intermediate between both; and some of the anatomists call it a neurochondrotic ligament. And this is a hard and cartilaginous ligament. And bone is the hardest of all thing...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.4282 |
| chrF++ | 0.6319 |
| METEOR | 0.5497 |
| ROUGE-L | 0.6704 |
| BERTScore | 0.9324 |
| COMET | 0.8080 |

**OPENAI**

> All membranes are already drier than the skin, as indeed are the meninges around the brain and the spinal cord—for these too are membranes. And likewise all ligaments, in proportion as they are harder than the skin, are to that extent also drier. The tendons too, even if they are softer than the ligaments, are at any rate clearly already harder than the skin. Cartilages come next after the ligaments and constitute a substance intermediate between the two; some anatomists call this a tendino-cartilaginous ligament. It is a ligament that is hard and cartilaginous. Bone, however, is the hardest o...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.4216 |
| chrF++ | 0.6183 |
| METEOR | 0.5474 |
| ROUGE-L | 0.6210 |
| BERTScore | 0.9308 |
| COMET | 0.8086 |

---

### Chunk 7

#### Source (Greek)

> δέδεικται γὰρ ἔμπροσθεν, ὡς τῶν γηρασκόντων ἅπαντα ξηραίνεται τὰ μόρια. γίγνεται δὲ πολλοῖς ὀστρακῶδες τὸ δέρμα πλέον ἢ δεῖ ξηρανθέν. ἐν τοιούτῳ δ’ οὐδὲν φύεσθαι δύναται, καθότι καὶ διὰ τῶν ἔμπροσθεν ὡμολόγηται. καὶ γὰρ δὴ καὶ τῶν χειρῶν τὰ ἔνδον ὥσπερ γε καὶ τὰ κάτω τῶν ποδῶν ἄτριχα καὶ ψιλὰ ξηρότητί τε καὶ πυκνότητι τοῦ κατ’ αὐτὰ τένοντος, ὃς ὑποτέτακται τῷ δέρματι. ὅσοις δ’ εἰς τέλος ξηρότητος οὐκ ἀφικνεῖται τὸ δέρμα τῆς κεφαλῆς, ἄρρωστοι τούτοις γίγνονται καὶ λευκαὶ πάντως αἱ τρίχες, ἃς ὀνομάζουσιν οἱ ἄνθρωποι πολιάς, ἄρρωστοι μὲν ἐνδείᾳ τῆς οἰκείας τροφῆς, λευκαὶ δέ, διότι καὶ τὸ τρέφον αὐτὰς τοιοῦτον οἷον εὐρώς τις φλέγματος ἐν χρόνῳ διασαπέντος. ὅταν γὰρ ὁ μὲν πόρος ἔτι μένῃ, τὸ περίττωμα δ’ ὀλίγον ᾖ καὶ γλίσχρον, ἀρρώστως δ’ ὑπὸ τῆς θερμασίας ὠθῆται πρόσω, πάσχει τι παραπλήσιον ἐν ...

#### Reference Translations

**Reference 1:**
> For it was shown previously that all the parts of those who are aging are dried out. In many the skin becomes shell-like being dried out more than it should be. In such skin, nothing is able to grow, as was also agreed upon through those things [said] previously. Furthermore also, the skin on the palms of the hands, just as that on the soles of the feet is hairless and bare due to dryness and thickness of the tendon in these which lies under the skin. The hair in those in whom the skin of the head does not reach complete dryness becomes weak and altogether white, which men term gray-haired; we...

**Reference 2:**
> (For it was shown previously that all parts of the body become drier in the process of aging.) And in many persons the skin becomes very hard through having been dried more than it should be; nothing can grow in such skin, as has been established in the above discussion. The palms of the hands, too, and the soles of the feet are hairless and bald, because of the dryness and thickness of the tendon in those parts, which is located immediately below the skin. Hair in people whose scalp does not reach perfect dryness becomes weak and wholly white, and is called ‘silver’; it becomes weak because o...

#### Model Translations & Scores

**CLAUDE**

> For it has been demonstrated previously that in those who are aging all the parts become dry. In many people the skin becomes more shell-like than it should, having been excessively dried. In such a condition nothing can grow, as has also been agreed upon in the preceding discussion. Indeed, the inner parts of the hands, just as the lower parts of the feet, are hairless and bare due to the dryness and density of the tendon beneath them, which lies under the skin. But in those whose scalp does not reach the final stage of dryness, the hairs become weak and entirely white, which people call grey...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3363 |
| chrF++ | 0.5554 |
| METEOR | 0.4819 |
| ROUGE-L | 0.5739 |
| BERTScore | 0.9206 |
| COMET | 0.8162 |

**GEMINI**

> For it has been shown previously that all the parts of those growing old become dry. And in many people, the skin, having been dried out more than is necessary, becomes like earthenware. And in such skin, nothing is able to grow, just as has also been acknowledged through the preceding arguments. For indeed, the inner parts of the hands, just like the lower parts of the feet, are hairless and bare due to both the dryness and the density of the tendon in those areas, which is situated beneath the skin. But for all those in whom the skin of the head does not reach a state of complete dryness, th...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3875 |
| chrF++ | 0.5962 |
| METEOR | 0.5491 |
| ROUGE-L | 0.5844 |
| BERTScore | 0.9168 |
| COMET | 0.8139 |

**OPENAI**

> For it has been shown above that in those who are growing old all the parts become dry. And in many the skin becomes potsherd-like, having been dried more than is fitting. In such a condition nothing can grow, as has also been agreed in the foregoing. For indeed the insides of the hands and likewise the undersides of the feet are hairless and bare because of the dryness and compactness of the tendon beneath them, which lies under the skin. But in those whose scalp does not reach the extreme of dryness, the hairs become diseased and altogether white—what people call grey hairs—diseased through ...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3230 |
| chrF++ | 0.5211 |
| METEOR | 0.5089 |
| ROUGE-L | 0.5189 |
| BERTScore | 0.9101 |
| COMET | 0.8055 |

---

### Chunk 8

#### Source (Greek)

> καὶ οἷς μὲν ἡ ῥὶς ὀξεῖα καὶ γρυπή, ξηροί, σιμῆς δ’ οὔσης ὑγροί· κατὰ ταὐτὰ δὲ καὶ περὶ τῶν ὀφθαλμῶν τε καὶ τῶν κροτάφων ἁπάντων τε τῶν ἄλλων μορίων. οἷς δ’ ἀνώμαλος ἡ κρᾶσις καὶ οὐχ ἡ αὐτὴ πάντων τῶν μερῶν, ἄτοπον ἐπὶ τούτων ἐξ ἑνὸς μορίου φύσεως ὑπὲρ ἁπάντων ἀποφαίνεσθαι. τοιοῦτον δέ τι τοὺς πλείστους αὐτῶν ἠπάτησεν, οὐχ ὑπὲρ τῶν ἀνθρώπων μόνον, ἀλλὰ καὶ περὶ τῶν ἄλλων ζῴων ἀποφήνασθαι τολμήσαντας ὑπὲρ ὅλης τῆς κράσεως ἐκ μόνων τῶν κατὰ τὸ δέρμα γνωρισμάτων. οὔτε γάρ, εἰ σκληρὸν τὸ δέρμα, ξηρὸν ἐξ ἀνάγκης τὸ ζῷον, ἀλλ’ ἐγχωρεῖ τὸ δέρμα μόνον, οὔτ’ εἰ μέλαν οὔτ’ εἰ δασύ. κατὰ δὲ τὸν αὐτὸν τρόπον οὐδ’ εἰ μαλακὸν ἢ λευκὸν ἢ ψιλὸν τριχῶν, ὑγρὸν ἐξ ἀνάγκης ὅλον τὸ ζῷον. ἀλλ’ εἰ μὲν ὁμαλῶς κέκραται σύμπαν, εὔλογόν ἐστιν, οἷόνπερ τὸ δέρμα, τοιοῦτον εἶναι καὶ τῶν ἄλλων ἕκαστον μορίων, εἰ δ’ ἀνωμά...

#### Reference Translations

**Reference 1:**
> And those in whom the nose is sharp or hooked are dry, while those in whom it is snub are wet. It is the same too regarding the eyes and the temples and all the other parts. On the other hand, in those in whom the krasis is non-uniform, and is not the same in all the parts, it is unwonted to make a statement about all the parts from the nature of one part. Such a thing deceives the majority of them, not only about humans, but also about the other animals, when they boldly make a statement about the whole krasis from the signs pertaining to the skin alone. For the animal is not necessarily dry,...

**Reference 2:**
> Then, too, a sharp, hooked nose will be dry, and those with a snub nose wet; and similarly as regards the eyes, the temples and all the other parts. But in cases where the mixture is uneven, and thus not the same in each part, it is incongruous to make assertions about all the parts on the basis of the nature of one. Such is the point on which most of them have been deceived: they presume to make assertions – not just in the case of humans, but with other animals too – about the whole mixture, solely on the basis of the indicators in the skin. And yet it does not necessarily follow from hardne...

#### Model Translations & Scores

**CLAUDE**

> And those in whom the nose is sharp and hooked are dry, but when it is snub-nosed they are moist; and the same applies concerning the eyes and the temples and all the other parts. But in those whose mixture is uneven and not the same in all parts, it is absurd in these cases to make a pronouncement about nature concerning all parts from a single part. Something of this sort has deceived most of them, who have dared to make pronouncements not only about human beings but also about other animals concerning the whole mixture from the signs in the skin alone. For neither if the skin is hard is the...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3320 |
| chrF++ | 0.5711 |
| METEOR | 0.4741 |
| ROUGE-L | 0.5745 |
| BERTScore | 0.9142 |
| COMET | 0.7804 |

**GEMINI**

> And those whose nose is sharp and hooked are dry, but if it is snub-nosed, they are moist. And the same holds true concerning the eyes, the temples, and all the other parts. But for those whose temperament is uneven and not the same in all their parts, it is absurd in these cases to make a pronouncement about the whole from the nature of a single part. But something of this sort has deceived most of them, who dared to make a pronouncement not only concerning humans but also about the other animals, regarding the entire temperament, on the basis of the characteristics of the skin alone. For an ...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3451 |
| chrF++ | 0.5593 |
| METEOR | 0.4471 |
| ROUGE-L | 0.5652 |
| BERTScore | 0.9119 |
| COMET | 0.7945 |

**OPENAI**

> Those whose nose is pointed and hooked are dry, whereas if it is snub they are moist; and the same applies to the eyes, the temples, and all the other parts. But in those whose mixture is irregular and not the same in all their parts, it is unreasonable to draw conclusions about the whole from the nature of a single part. A mistake of this sort has misled most of them, who have ventured to pronounce not only about human beings but also about other animals regarding the entire mixture on the basis solely of the signs furnished by the skin. For neither, if the skin is hard, is the animal of nece...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2760 |
| chrF++ | 0.4975 |
| METEOR | 0.4096 |
| ROUGE-L | 0.5077 |
| BERTScore | 0.8983 |
| COMET | 0.7837 |

---

### Chunk 9

#### Source (Greek)

> καὶ τὸ τῆς Μηδείας δὲ φάρμακον τοιοῦτον ἦν. πάντα γοῦν ἀνάπτεται προσβαλλούσης θερμασίας οἷς ἂν ἐπαλειφθῇ. σκευάζεται δ’ ἐκεῖνο διά τε θείου καὶ τῆς ὑγρᾶς ἀσφάλτου. καὶ μὲν δὴ καὶ ὡς θαῦμά τις ἐδείκνυ· ἀποσβεννὺς λύχνον αὖθις ἧπτε τοίχῳ προσφέρων· ἕτερος δὲ λίθῳ προσέφερεν· ἐτεθείωτο δ’ ἄρα καὶ ὁ τοῖχος καὶ ὁ λίθος. καὶ ὡς ἐγνώσθη τοῦτο, θαυμαστὸν οὐκέτ’ ἦν τὸ γιγνόμενον. Πάντ’ οὖν ταῦτα τὰ φάρμακα θερμὰ μὲν οὔπω τελέως ἐστίν, ἐπιτηδειότατα μέντοι πρὸς τὸ γενέσθαι θερμὰ καὶ διὰ τοῦτο δυνάμει θερμὰ λέγεται. περὶ μὲν δὴ τούτων οὐδὲν ἄπορον, ἀλλ’ οὐδὲ διὰ τί πινόμενος μὲν ὁ οἶνος ἱκανῶς θερμαίνει τὸ σῶμα, κατὰ δὲ τοῦ δέρματος ἐπιτιθέμενος οὐ θερμαίνει. δέδεικται γὰρ ὀλίγῳ πρότερον οὐχ ἁπλῶς ὡς θερμὸν φάρμακον ἀλλ’ ὡς οἰκεία τροφὴ θερμαίνων τὸ ζῷον. ὡς γὰρ αἱ τοῦ πυρὸς ἐπιτήδειοι τροφαὶ τὸ πῦρ...

#### Reference Translations

**Reference 1:**
> And the medication of Medea was of this sort. At all events, anything that it is smeared over is kindled to flame when heat is applied to it. And that is prepared from brimstone and the liquid of asphalt. Furthermore also, what is shown as a mystery is an extinguished lamp that is set alight again when brought together with a wall, and another when brought together with a stone. The wall and the stone were in fact covered with brimstone. And when this was known, the occurrence was no longer surprising. Thus all these medications are not yet completely hot, but are of course very suited to beco...

**Reference 2:**
> Medea’s drug was something of this sort, too. Anything into which [this] has been rubbed catches fire when heat is brought into contact with it. That, in fact, is prepared from a mixture of brimstone and wet asphalt. Indeed, this used to be shown off as a magic trick: one would extinguish a lamp and then light it again by bringing it into contact with a wall, or sometimes with a stone. The wall or stone had of course been covered in brimstone; and once this was realized the thing no longer appeared amazing. So, all these drugs are not yet completely hot, but have to a high degree a tendency to...

#### Model Translations & Scores

**CLAUDE**

> And the drug of Medea was of such a nature. At any rate, everything to which it is applied bursts into flame when heat is brought near. That drug is prepared from sulfur and liquid asphalt. And indeed someone used to display it as a marvel: after extinguishing a lamp he would light it again by bringing it near a wall; another would bring it near a stone; for both the wall and the stone had been treated with sulfur. And when this was understood, what occurred was no longer marvelous. All these drugs, therefore, are not yet completely hot, but they are most suitable for becoming hot, and for thi...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3307 |
| chrF++ | 0.5267 |
| METEOR | 0.4972 |
| ROUGE-L | 0.5059 |
| BERTScore | 0.9125 |
| COMET | 0.8011 |

**GEMINI**

> And the drug of Medea was also of such a kind. For indeed, everything with which it might be smeared is ignited when heat is applied. And that substance is prepared from both sulfur and liquid asphalt. And indeed, someone was demonstrating it as a marvel: extinguishing a lamp, he would light it again by bringing it near a wall; and another would bring it near a stone. For, as it turned out, both the wall and the stone had been treated with sulfur. And when this became known, what was happening was no longer marvelous.

All these drugs, therefore, are not yet completely hot, but they are most s...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2955 |
| chrF++ | 0.5498 |
| METEOR | 0.4695 |
| ROUGE-L | 0.5331 |
| BERTScore | 0.9160 |
| COMET | 0.8019 |

**OPENAI**

> And the drug of Medea was of such a sort. For, at any rate, everything is kindled when heat is applied to whatever has been smeared with it. That preparation is made by means of sulfur and liquid bitumen. Indeed, someone even used to exhibit it as a wonder: having extinguished a lamp, he would light it again by bringing it near a wall; another would bring it near a stone; and it turned out that both the wall and the stone had been sulfurized. Once this was recognized, the occurrence was no longer marvelous. All these drugs, then, are not yet completely hot, but are most apt to become hot; and ...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.3359 |
| chrF++ | 0.5249 |
| METEOR | 0.4772 |
| ROUGE-L | 0.5134 |
| BERTScore | 0.9146 |
| COMET | 0.7972 |

---

### Chunk 10

#### Source (Greek)

> ἂν γὰρ οὕτω σμικρά τινα περὶ ἡμᾶς ᾖ πάθη διὰ παντός, ὡς μηδεμίαν αἰσθητὴν καὶ σαφῆ βλάβην ἐνεργείας ἐργάζεσθαι μηδεμιᾶς, εὐκαταφρόνητα δήπουθέν ἐστι καὶ τῷ μηδ’ εἶναι φάσκοντι τὰ τοιαῦτα συγχωρητέον. οὕτως οὖν ἔχει κἀπὶ τῶν τρεφόντων ὀλίγου δεῖν ἁπάντων. ἐργάζεται μὲν γάρ τι καὶ αὐτὰ περὶ τὸ σῶμα τῶν ἀνθρώπων, ἀλλ’ οὐκ αἰσθητὸν οὐδὲ σαφὲς εἰσάπαξ. ἡ μέντοι πολυχρόνιος αὐτῶν προσφορὰ μεγάλως ἀλλοιοῖ καὶ μεταβάλλει σαφῶς ἤδη τὰ σώματα. ἔνια μέν γε καὶ κατὰ τὴν πρώτην χρῆσιν εὐθὺς ἐναργῶς ἐνδείκνυται τὴν ἀλλοίωσιν, οἷον καὶ ἡ θριδακίνη τοὺς μὲν ἐγκαιομένους τὴν γαστέρα σαφῶς ἐμψύχουσά τε καὶ ἀδίψους ἐργαζομένη, τοὺς δὲ κατεψυγμένους ἐναργῶς βλάπτουσα. συντελεῖ δ’ οὐ σμικρὰ καὶ τοῖς ὕπνοις οὐ κατ’ ἄλλον τινὰ λόγον, ἀλλ’ ἢ ὅτι ψυχρά τ’ ἐστὶ καὶ ὑγρὰ τὴν κρᾶσιν, ἀλλ’ οὕτω ψυχρὰ καὶ ὑγρὰ πρὸς ἄνθ...

#### Reference Translations

**Reference 1:**
> For in this way, there would be certain small affections involving us continuously, such as to produce no perceptible and clear harm to any functions, and are, I presume, to be ignored. As a result one must agree with someone who says such things don’t exist. It is the same in the case of all nutriments apart from a few. That is to say, these also produce something involving the body of humans, but not something perceptible or clear once and for all. Nevertheless, the administration of these over a long period of time greatly alters and already clearly changes the bodies. Some, in fact, at the...

**Reference 2:**
> For if we are constantly suffering from certain ailments that are so tiny that they produce no clear, perceptible harm to our activities, then, surely, these may rightly be ignored, and we may agree with the person who denies also that they exist. It is so too with almost all things that nourish. These also have some effect on the human body, but this effect is not at once clear nor perceptible. Their use over a long period, however, brings about great alteration and obvious actual change in our bodies. Some of them, indeed, show manifest indications of alteration even at the first use; lettuc...

#### Model Translations & Scores

**CLAUDE**

> For if certain affections concerning us are so small throughout as to produce no perceptible and clear harm to any activity, they are surely to be despised and one must concede to him who asserts that such things do not even exist. Thus it stands also in the case of almost all nourishing substances. For they too produce some effect upon the human body, but not one that is perceptible or clear all at once. However, their prolonged consumption greatly alters and changes the bodies in a now clearly evident way. Some indeed even at their first use immediately show the alteration clearly, as for in...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2900 |
| chrF++ | 0.5389 |
| METEOR | 0.4814 |
| ROUGE-L | 0.5179 |
| BERTScore | 0.9110 |
| COMET | 0.7880 |

**GEMINI**

> For if certain affections upon us should be so small continually as to produce no perceptible and clear harm to any activity, they are, I suppose, easily disregarded, and one must concede to the one who asserts that such things do not even exist. So it is, then, in the case of almost all nutritive substances. For they too produce some effect upon the human body, but it is not perceptible or clear at once. The long-continued ingestion of them, however, greatly alters and changes the bodies, now in a clear manner. Some, at least, even upon the first use, immediately and manifestly display the al...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2852 |
| chrF++ | 0.5534 |
| METEOR | 0.5074 |
| ROUGE-L | 0.5234 |
| BERTScore | 0.9098 |
| COMET | 0.8086 |

**OPENAI**

> For if there are continually certain slight affections in relation to us, such that they produce no perceptible and distinct harm to any function, they are, of course, easily disregarded, and one must even concede to the person who claims that such things do not exist. Thus it is with almost all things that nourish. They too produce some effect upon the human body, but not at once in a perceptible or clear fashion. Yet their long-continued application greatly alters and now clearly transforms bodies. Some, to be sure, even on first use immediately display the alteration plainly—for example let...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2637 |
| chrF++ | 0.5248 |
| METEOR | 0.4608 |
| ROUGE-L | 0.4795 |
| BERTScore | 0.9107 |
| COMET | 0.7829 |

---
