import torch
import torch.nn as nn
import torch.nn.functional as F


class VGG13_16x(nn.Module):
    def __init__(self, in_channl):
        super(VGG13_16x, self).__init__()
        self.stage_1 = nn.Sequential(
            nn.Conv2d(in_channl, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )

        self.stage_2 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )

        self.stage_3 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            # nn.MaxPool2d(2,2),
        )

        self.stage_4 = nn.Sequential(
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )

        self.stage_5 = nn.Sequential(
            # 空洞卷积
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=2, dilation=2),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=2, dilation=2),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=2, dilation=2),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )

    def forward(self, x):
        x1 = self.stage_1(x)
        x2 = self.stage_2(x1)
        x3 = self.stage_3(x2)
        x4 = self.stage_4(x3)
        x5 = self.stage_5(x4)
        return [x1, x2, x3, x4, x5]


class DoubleConv(nn.Module):
    """
    (convolution => [BN] => ReLU) * 2
    """

    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)


class Up(nn.Module):
    """
    Upscaling then double conv
    """

    def __init__(self, in_channels, out_channels, bilinear=True):
        super().__init__()

        # if bilinear, use the normal convolutions to reduce the number of channels
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        else:
            self.up = nn.ConvTranspose2d(in_channels // 2, in_channels // 2, kernel_size=2, stride=2)

        self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1, x2):
        x1 = self.up(x1)
        # input is CHW
        diffY = torch.tensor([x2.size()[2] - x1.size()[2]])
        diffX = torch.tensor([x2.size()[3] - x1.size()[3]])

        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
                        diffY // 2, diffY - diffY // 2])
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class OutConv(nn.Module):
    def __init__(self, in_channels, out_channels, bilinear=True):
        super().__init__()

        # if bilinear, use the normal convolutions to reduce the number of channels
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        else:
            self.up = nn.ConvTranspose2d(in_channels // 2, in_channels // 2, kernel_size=2, stride=2)
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        x = self.up(x)
        return self.conv(x)


class OutConv1(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()

        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):

        return self.conv(x)


class ASPP_module(nn.ModuleList):
    def __init__(self, in_channels, out_channels, dilation_list=[6, 12, 18, 24]):
        super(ASPP_module, self).__init__()
        self.dilation_list = dilation_list
        for dia_rate in self.dilation_list:
            self.append(
                nn.Sequential(
                    nn.Conv2d(in_channels, out_channels, kernel_size=1 if dia_rate == 1 else 3, dilation=dia_rate,
                              padding=0 if dia_rate == 1 else dia_rate),
                    nn.BatchNorm2d(out_channels),
                    nn.ReLU()
                )
            )

    def forward(self, x):
        outputs = []
        for aspp_module in self:
            outputs.append(aspp_module(x))
        return torch.cat(outputs, 1)


class UNet_X(nn.Module):
    def __init__(self, n_channels, n_classes, bilinear=True):
        super(UNet_X, self).__init__()
        print("使用UNet_X网络训练：\n")
        self.backbone = VGG13_16x(n_channels)
        self.n_channels = n_channels
        self.num_classes = n_classes
        self.bilinear = bilinear

        self.up1 = Up(1792, 896, self.bilinear)  # 256
        self.up2 = Up(1152, 576, self.bilinear)
        self.up3 = Up(704, 352, self.bilinear)
        self.up4 = Up(416, 208, self.bilinear)
        self.outc1 = OutConv(208, 64, self.bilinear)
        self.outc = OutConv1(64, self.num_classes)

        self.ASPP_module = ASPP_module(512, 256, [1, 6, 12, 18])

        self.avg_pool = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(512, 256, 1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True))

    def forward(self, x):
        x1 = self.backbone.stage_1(x)  # 64
        x2 = self.backbone.stage_2(x1)  # 128
        x3 = self.backbone.stage_3(x2)  # 256
        x4 = self.backbone.stage_4(x3)  # 512
        x5 = self.backbone.stage_5(x4)  # 1024

        x_1_5 = self.ASPP_module(x5)  # 256
        x_2_5 = nn.functional.interpolate(self.avg_pool(x5), size=(x5.size(2), x5.size(3)), mode='bilinear',
                                          align_corners=True)  # 256
        x0 = torch.cat([x_1_5, x_2_5], 1)  # 512

        out = self.up1(x0, x4)  # 256
        out = self.up2(out, x3)  # 128
        out = self.up3(out, x2)  # 64
        out = self.up4(out, x1)  # 64
        out = self.outc1(out)
        logits = self.outc(out)
        return logits
