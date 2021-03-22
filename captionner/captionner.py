import torch.nn as nn
import torchvision.models as models
import spacy  # for tokenizer
import torch
from PIL import Image
import torchvision.transforms as transforms
import pickle

# python -m spacy download en
spacy_eng = spacy.load('en_core_web_sm')


class Vocab_Builder:

    def __init__(self, freq_threshold):

        # freq_threshold is to allow only words with a frequency higher
        # than the threshold

        self.itos = {0: "<PAD>", 1: "<SOS>", 2: "<EOS>", 3: "<UNK>"}  # index to string mapping
        self.stoi = {"<PAD>": 0, "<SOS>": 1, "<EOS>": 2, "<UNK>": 3}  # string to index mapping
        self.freq_threshold = freq_threshold

    def __len__(self):
        return len(self.itos)

    @staticmethod
    def tokenizer_eng(text):
        # Removing spaces, lower, general vocab related work

        return [token.text.lower() for token in spacy_eng.tokenizer(text)]

    def build_vocabulary(self, sentence_list):
        frequencies = {}  # dict to lookup for words
        idx = 4

        # FIXME better ways to do this are there
        for sentence in sentence_list:
            for word in self.tokenizer_eng(sentence):
                if word not in frequencies:
                    frequencies[word] = 1
                else:
                    frequencies[word] += 1
                if (frequencies[word] == self.freq_threshold):
                    # Include it
                    self.stoi[word] = idx
                    self.itos[idx] = word
                    idx += 1

    # Convert text to numericalized values
    def numericalize(self, text):
        tokenized_text = self.tokenizer_eng(text)  # Get the tokenized text

        # Stoi contains words which passed the freq threshold. Otherwise, get the <UNK> token
        return [self.stoi[token] if token in self.stoi else self.stoi["<UNK>"]
                for token in tokenized_text]

    def denumericalize(self, tensors):
        text = [self.itos[token] if token in self.itos else self.itos[3]]
        return text



class EncoderCNN(nn.Module):
    def __init__(self, embed_size=256, train_CNN=False):
        super(EncoderCNN, self).__init__()
        self.train_CNN = train_CNN
        self.resnet50 = models.resnet50(pretrained=True)

        for name, param in self.resnet50.named_parameters():
            if "fc.weight" in name or "fc.bias" in name:
                param.requires_grad = True
            else:
                param.requires_grad = self.train_CNN

        in_features = self.resnet50.fc.in_features

        modules = list(self.resnet50.children())[:-1]
        self.resnet50 = nn.Sequential(*modules)

        self.fc = nn.Linear(in_features, embed_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)

    def forward(self, images):
        # Fine tuning, we don't want to train
        features = self.resnet50(images)
        features = features.view(features.size(0), -1)
        features = self.fc(features)
        return features


class DecoderRNN(nn.Module):
    def __init__(self, embed_size, hidden_size, vocab_size, num_layers):
        super(DecoderRNN, self).__init__()
        self.embed = nn.Embedding(vocab_size, embed_size)  # Embedding layer courtesy Pytorch
        self.lstm = nn.LSTM(embed_size, hidden_size, num_layers)
        self.linear = nn.Linear(hidden_size, vocab_size)
        self.dropout = nn.Dropout(0.5)

        # output from lstm is mapped to vocab size

    def forward(self, features, captions):
        embeddings = self.dropout(self.embed(captions))

        # Add an additional dimension so it's viewed as a time step, (N, M ) -- > (1, N, M) * t , t timesteps
        embeddings = torch.cat((features.unsqueeze(0), embeddings), dim=0)
        hiddens, _ = self.lstm(embeddings)
        # Take the hidden state, _ unimportant

        outputs = self.linear(hiddens)

        return outputs


class CNNtoRNN(nn.Module):
    def __init__(self, embed_size, hidden_size, vocab_size, num_layers):
        super(CNNtoRNN, self).__init__()
        self.encoderCNN = EncoderCNN(embed_size)
        self.decoderRNN = DecoderRNN(embed_size, hidden_size, vocab_size, num_layers)

    def forward(self, images, captions):
        features = self.encoderCNN(images)
        outputs = self.decoderRNN(features, captions)
        return outputs

    def caption_image(self, image, vocabulary, max_length=50):
        # Getting the damn caption
        result_caption = []
        with torch.no_grad():
            x = self.encoderCNN(image).unsqueeze(0)
            states = None

            for _ in range(max_length):
                hiddens, states = self.decoderRNN.lstm(x, states)
                output = self.decoderRNN.linear(hiddens.squeeze(0))
                predicted = output.argmax(1)

                result_caption.append(predicted.item())  # item is used to get python scalar from cuda object
                x = self.decoderRNN.embed(predicted).unsqueeze(0)

                if vocabulary.itos[predicted.item()] == "<EOS>":  # break when end of sequence
                    break
        return [vocabulary.itos[idx] for idx in result_caption]  # returns the actual sentence


mean = [0.485, 0.456, 0.406]
std = [0.229, 0.224, 0.225]


class Captionner():
    transform = None
    model = None

    def __init__(self, base_path, model_name, vocab_name):
        with open(base_path + vocab_name, 'rb') as f:
            self.vocab = pickle.load(f)

        torch.backends.cudnn.benchmark = True  # Get some boost probaby
        device = torch.device("cpu")

        self.model = CNNtoRNN(256, 256, len(self.vocab), 2).to(device)
        self.model.load_state_dict(torch.load(base_path + model_name, map_location='cpu')["state_dict"])
        self.transform = transforms.Compose(
            [transforms.Resize((256, 256)),
             transforms.ToTensor(),
             transforms.Normalize(mean, std)]
            )

    def caption(self, image_path: str) -> str:
        image = Image.open(image_path).convert('RGB')
        image = self.transform(image)

        self.model.eval()
        with torch.no_grad():
            caps = self.model.caption_image(torch.reshape(image, (1, 3, 256, 256)), vocabulary=self.vocab)
            caption = ' '.join(caps)
            print(caption)
            return caption[5:-5]
