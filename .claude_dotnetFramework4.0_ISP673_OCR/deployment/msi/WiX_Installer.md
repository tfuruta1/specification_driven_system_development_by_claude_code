# WiX Toolset MSIインストーラー設定

## 概要
WiX Toolsetを使用してISP-673 OCRアプリケーションのMSIインストーラーを作成します。

## Product.wxs サンプル

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="ISP-673 OCR Application" 
           Language="1041" 
           Version="1.0.0.0" 
           Manufacturer="Your Company" 
           UpgradeCode="{PUT-GUID-HERE}">
    
    <Package InstallerVersion="200" 
             Compressed="yes" 
             InstallScope="perMachine" 
             Platform="x86" />

    <MajorUpgrade DowngradeErrorMessage="新しいバージョンが既にインストールされています。" />
    <MediaTemplate EmbedCab="yes" />

    <!-- .NET Framework 4.0 チェック -->
    <PropertyRef Id="NETFRAMEWORK40FULL"/>
    <Condition Message="このアプリケーションには .NET Framework 4.0 が必要です。">
      <![CDATA[Installed OR NETFRAMEWORK40FULL]]>
    </Condition>

    <Feature Id="ProductFeature" Title="ISP-673 OCR" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
      <ComponentGroupRef Id="COMComponents" />
    </Feature>
  </Product>

  <Fragment>
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="ISP673_OCR" />
      </Directory>
    </Directory>
  </Fragment>

  <Fragment>
    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <Component Id="MainExecutable" Guid="{PUT-GUID-HERE}">
        <File Id="ISP673_OCRApp.exe" 
              Source="$(var.ISP673_OCRApp.TargetPath)" 
              KeyPath="yes" />
      </Component>
    </ComponentGroup>
    
    <ComponentGroup Id="COMComponents" Directory="INSTALLFOLDER">
      <Component Id="GloryOcrCOM" Guid="{PUT-GUID-HERE}">
        <File Id="GloryOcrMain4.dll" 
              Source="Redist\GloryOcrMain4.dll" 
              KeyPath="yes" />
        <!-- COM登録 -->
        <RegistryValue Root="HKCR" 
                       Key="CLSID\{ISP673-OCR-CLSID}" 
                       Value="GloryOcr4Lib" 
                       Type="string" />
      </Component>
    </ComponentGroup>
  </Fragment>
</Wix>
```

## ビルドコマンド
```cmd
candle.exe Product.wxs -arch x86
light.exe Product.wixobj -ext WixUIExtension -out ISP673_OCR.msi
```