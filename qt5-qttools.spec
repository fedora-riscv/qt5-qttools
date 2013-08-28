
%global qt_module qttools
%global system_clucene 1

Summary: Qt5 - QtTool components 
Name:    qt5-qttools
Version: 5.0.2
Release: 4%{?dist}

# See LGPL_EXCEPTIONS.txt, LICENSE.GPL3, respectively, for exception details
License: LGPLv2 with exceptions or GPLv3 with exceptions
Url: http://qt-project.org/
Source0: http://download.qt-project.org/archive/qt/5.0/%{version}/submodules/%{qt_module}-opensource-src-%{version}.tar.xz

Patch1: qttools-system_clucene.patch

Source20: assistant.desktop
Source21: designer.desktop
Source22: linguist.desktop
Source23: qdbusviewer.desktop

BuildRequires: desktop-file-utils
BuildRequires: qt5-qtbase-devel >= %{version}
BuildRequires: qt5-qtbase-static
%if 0%{?system_clucene}
BuildRequires: clucene09-core-devel
%endif

%{?_qt5_version:Requires: qt5-qtbase%{?_isa} >= %{_qt5_version}}

Provides: qt5-assistant = %{version}-%{release}
Provides: qt5-qdbusviewer = %{version}-%{release}

%description 
%{summary}.

%package devel
Summary: Development files for %{name} 
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: qt5-qtbase-devel%{?_isa}
Provides: qt5-designer = %{version}-%{release}
Provides: qt5-linguist = %{version}-%{release}
%description devel
%{summary}.

%package static
Summary: Static library files for %{name}
Requires: %{name}-devel%{?_isa} = %{version}-%{release}
%description static
%{summary}.


%prep
%setup -q -n qttools-opensource-src-%{version}%{?pre:-%{pre}}

%if 0%{?system_clucene}
%patch1 -p1 -b .system_clucene
# bundled libs
#mv src/assistant/3rdparty/clucene \
#   src/assistant/3rdparty/clucene.BAK
%endif


%build
%{_qt5_qmake}

make %{?_smp_mflags}


%install
make install INSTALL_ROOT=%{buildroot}

# Add desktop files, --vendor=qt4 helps avoid possible conflicts with qt3/qt4
desktop-file-install \
  --dir=%{buildroot}%{_datadir}/applications \
  --vendor="qt5" \
  %{SOURCE20} %{SOURCE21} %{SOURCE22} %{SOURCE23}

# icons
install -m644 -p -D src/assistant/assistant/images/assistant.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/assistant-qt5.png
install -m644 -p -D src/assistant/assistant/images/assistant-128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/assistant-qt5.png
install -m644 -p -D src/designer/src/designer/images/designer.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/designer-qt5.png
install -m644 -p -D src/qdbus/qdbusviewer/images/qdbusviewer.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/qdbusviewer-qt5.png
install -m644 -p -D src/qdbus/qdbusviewer/images/qdbusviewer-128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/qdbusviewer-qt5.png
# linguist icons
for icon in src/linguist/linguist/images/icons/linguist-*-32.png ; do
  size=$(echo $(basename ${icon}) | cut -d- -f2)
  install -p -m644 -D ${icon} %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/linguist.png
done

# put non-conflicting binaries with -qt5 postfix in %%{_bindir} 
mkdir %{buildroot}%{_bindir}
pushd %{buildroot}%{_qt5_bindir}
for i in * ; do
  case "${i}" in
   assistant|designer|lconvert|linguist|lrelease|lupdate|pixeltool|qcollectiongenerator|qdbus|qdbusviewer|qhelpconverter|qhelpgenerator)
      mv $i ../../../bin/${i}-qt5
      ln -s ../../../bin/${i}-qt5 .
      ln -s ../../../bin/${i}-qt5 $i
      ;;
   *)
      mv $i ../../../bin/
      ln -s ../../../bin/$i .
      ;;
  esac
done
popd

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
pushd %{buildroot}%{_qt5_libdir}
for prl_file in libQt5*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  if [ -f "$(basename ${prl_file} .prl).so" ]; then
    rm -fv "$(basename ${prl_file} .prl).la"
    sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
  fi
done
popd


%post
/sbin/ldconfig
touch --no-create %{_datadir}/icons/hicolor ||:

%posttrans
gtk-update-icon-cache -q %{_datadir}/icons/hicolor 2> /dev/null ||:

%postun
/sbin/ldconfig
if [ $1 -eq 0 ] ; then
touch --no-create %{_datadir}/icons/hicolor ||:
gtk-update-icon-cache -q %{_datadir}/icons/hicolor 2> /dev/null ||:
fi

%files 
%{_bindir}/assistant*
%{_bindir}/qdbus*
%{_bindir}/qdbusviewer*
%{_qt5_bindir}/assistant*
%{_qt5_bindir}/qdbus*
%{_qt5_bindir}/qdbusviewer*
%{_qt5_libdir}/libQt5CLucene.so.5*
%{_qt5_libdir}/libQt5Designer.so.5*
%{_qt5_libdir}/libQt5DesignerComponents.so.5*
%{_qt5_libdir}/libQt5Help.so.5*
%{_qt5_datadir}/phrasebooks/
%{_datadir}/applications/*assistant.desktop
%{_datadir}/applications/*qdbusviewer.desktop
%{_datadir}/icons/hicolor/*/apps/assistant*.*
%{_datadir}/icons/hicolor/*/apps/qdbusviewer*.*

%post devel 
touch --no-create %{_datadir}/icons/hicolor ||:

%posttrans devel 
gtk-update-icon-cache -q %{_datadir}/icons/hicolor 2> /dev/null ||:
update-desktop-database -q &> /dev/null ||:

%postun devel 
if [ $1 -eq 0 ] ; then
touch --no-create %{_datadir}/icons/hicolor ||:
gtk-update-icon-cache -q %{_datadir}/icons/hicolor 2> /dev/null ||:
fi

%files devel
%{_bindir}/designer*
%{_bindir}/lconvert*
%{_bindir}/linguist*
%{_bindir}/lrelease*
%{_bindir}/lupdate*
%{_bindir}/pixeltool*
%{_bindir}/qcollectiongenerator*
%{_bindir}/qhelpconverter*
%{_bindir}/qhelpgenerator*
%{_qt5_bindir}/designer*
%{_qt5_bindir}/lconvert*
%{_qt5_bindir}/linguist*
%{_qt5_bindir}/lrelease*
%{_qt5_bindir}/lupdate*
%{_qt5_bindir}/pixeltool*
%{_qt5_bindir}/qcollectiongenerator*
%{_qt5_bindir}/qhelpconverter*
%{_qt5_bindir}/qhelpgenerator*
%{_qt5_headerdir}/Qt*/
%{_qt5_libdir}/libQt5CLucene.prl
%{_qt5_libdir}/libQt5CLucene.so
%{_qt5_libdir}/libQt5Designer*.prl
%{_qt5_libdir}/libQt5Designer*.so
%{_qt5_libdir}/libQt5Help.prl
%{_qt5_libdir}/libQt5Help.so
%{_qt5_libdir}/cmake/Qt5*/
%{_qt5_libdir}/pkgconfig/Qt5*.pc
%{_qt5_archdatadir}/mkspecs/modules/*.pri
%{_datadir}/applications/*designer.desktop
%{_datadir}/applications/*linguist.desktop
%{_datadir}/icons/hicolor/*/apps/designer*.*
%{_datadir}/icons/hicolor/*/apps/linguist*.*

%files static
%{_qt5_libdir}/libQt5UiTools.*a
%{_qt5_libdir}/libQt5UiTools.prl


%changelog
* Mon Aug 19 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-4
- use system clucene09-core

* Mon Apr 29 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-3
- drop deprecated Encoding= key from .desktop files
- add justification for desktop vendor usage

* Fri Apr 19 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-2
- add .desktop/icons for assistant, designer, linguist, qdbusviewer

* Thu Apr 11 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-1
- 5.0.2

* Mon Feb 25 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.1-2
- BR: pkgconfig(zlib)
- -static subpkg

* Sat Feb 23 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.1-1
- first try

