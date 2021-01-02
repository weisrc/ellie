import tensorflow_text
import tensorflow_hub as hub
import fasttext
# import multi_rake

# rake_model = multi_rake.Rake()

fasttext_model = fasttext.load_model("models/fasttext.ftz")


# def getkw(sample):
#     res = rake_model.apply(sample)
#     return [t[0] for t in res]


def langid(sample):
    return fasttext_model.predict(sample)[0][0][-2:]


embed = hub.load("models/use")
