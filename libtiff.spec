# libtiff is used by wine
%ifarch %{x86_64}
%bcond_without compat32
%endif

%define major 6
%define libname %mklibname tiff
%define libxx %mklibname tiffxx
%define devname %mklibname tiff -d
%define lib32name %mklib32name tiff
%define lib32xx %mklib32name tiffxx
%define dev32name %mklib32name tiff -d
%bcond_without bootstrap

%global optflags %{optflags} -O3

# (tpg) enable PGO build
%bcond_without pgo

#define beta rc1

Summary:	A library of functions for manipulating TIFF format image files
Name:		libtiff
Version:	4.6.0
Release:	%{?beta:0.%{beta}.}1
License:	BSD-like
Group:		System/Libraries
Url:		http://libtiff.maptools.org/
Source0:	http://download.osgeo.org/libtiff/tiff-%{version}%{?beta:%{beta}}.tar.gz
Patch1:		tiff-3.9.1-no_contrib.diff
BuildRequires:	libtool
BuildRequires:	jbig-devel
BuildRequires:	pkgconfig(libjpeg)
BuildRequires:	pkgconfig(libzstd)
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	pkgconfig(ice)
%if %{without bootstrap}
BuildRequires:	pkgconfig(glut)
BuildRequires:	pkgconfig(glu)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(libwebp)
%endif
BuildRequires:	pkgconfig(zlib)
%if %{with compat32}
BuildRequires:	libc6
BuildRequires:	devel(libjpeg)
BuildRequires:	devel(libzstd)
BuildRequires:	devel(liblzma)
BuildRequires:	devel(libICE)
BuildRequires:	devel(libGL)
BuildRequires:	devel(libGLU)
%endif

%description
The libtiff package contains a library of functions for manipulating TIFF
(Tagged Image File Format) image format files. TIFF is a widely used file
format for bitmapped images. TIFF files usually end in the .tif extension
and they are often quite large.

%package progs
Summary:	Binaries needed to manipulate TIFF format image files
Group:		Graphics

%description progs
This package provides binaries needed to manipulate TIFF format image files.

%package -n %{libname}
Summary:	A library of functions for manipulating TIFF format image files
Group:		System/Libraries

%description -n %{libname}
The libtiff package contains a library of functions for manipulating TIFF
(Tagged Image File Format) image format files. TIFF is a widely used file
format for bitmapped images. TIFF files usually end in the .tif extension
and they are often quite large.

%package -n %{libxx}
Summary:	A library of functions for manipulating TIFF format image files
Group:		System/Libraries
Conflicts:	%{_lib}tiff5 < 4.0.3-2

%description -n %{libxx}
This package contains a shared library for %{name}.

%package -n %{devname}
Summary:	Development tools for programs which will use the libtiff library
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Requires:	%{libxx} = %{version}-%{release}
Provides:	tiff-devel = %{version}-%{release}
Requires:	pkgconfig(libzstd)
Requires:	pkgconfig(liblzma)
Requires:	pkgconfig(libjpeg)
Requires:	pkgconfig(zlib)

%description -n %{devname}
This package contains the header files and .so libraries for developing
programs which will manipulate TIFF format image files using the libtiff
library.

%if %{with compat32}
# lib32name == name
%if 0
%package -n %{lib32name}
Summary:	A library of functions for manipulating TIFF format image files (32-bit)
Group:		System/Libraries

%description -n %{lib32name}
The libtiff package contains a library of functions for manipulating TIFF
(Tagged Image File Format) image format files. TIFF is a widely used file
format for bitmapped images. TIFF files usually end in the .tif extension
and they are often quite large.
%endif

%package -n %{lib32xx}
Summary:	A library of functions for manipulating TIFF format image files (32-bit)
Group:		System/Libraries
Conflicts:	%{_lib}tiff5 < 4.0.3-2

%description -n %{lib32xx}
This package contains a shared library for %{name}.

%package -n %{dev32name}
Summary:	Development tools for programs which will use the libtiff library (32-bit)
Group:		Development/C
Requires:	%{devname} = %{version}-%{release}
Requires:	%{lib32name} = %{version}-%{release}
Requires:	%{lib32xx} = %{version}-%{release}
Requires:	devel(libzstd)
Requires:	devel(liblzma)
Requires:	devel(libjpeg)
Requires:	devel(libz)

%description -n %{dev32name}
This package contains the header files and .so libraries for developing
programs which will manipulate TIFF format image files using the libtiff
library.
%endif

%prep
%autosetup -n tiff-%{version} -p1

# cleanup
for i in $(find . -type d -name CVS) $(find . -type f -name .cvs\*) $(find . -type f -name .#\*); do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

# Use build system's libtool.m4, not the one in the package.
rm -f libtool.m4
autoreconf -fi

%build
export CONFIGURE_TOP="$(pwd)"
%if %{with compat32}
mkdir build32
cd build32
%configure32 \
	--enable-ld-version-script
%make_build
cd ..
%endif

mkdir buildnative
cd buildnative

%if %{with pgo}
export LD_LIBRARY_PATH="$(pwd)"

CFLAGS="%{optflags} -fprofile-generate" \
CXXFLAGS="%{optflags} -fprofile-generate" \
LDFLAGS="%{build_ldflags} -fprofile-generate" \
%configure \
	--disable-static \
	--enable-ld-version-script

%make_build
make check

unset LD_LIBRARY_PATH
llvm-profdata merge --output=%{name}-llvm.profdata $(find . -name "*.profraw" -type f)
PROFDATA="$(realpath %{name}-llvm.profdata)"
rm -f *.profraw
make clean

CFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
CXXFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
LDFLAGS="%{build_ldflags} -fprofile-use=$PROFDATA" \
%endif
%configure \
	--disable-static \
	--enable-ld-version-script

%make_build

%install
mkdir -p %{buildroot}/{%{_bindir},%{_datadir}}
rm -rf installed_docs

%if %{with compat32}
%make_install -C build32
%endif
%make_install -C buildnative

install -m0644 libtiff/tiffiop.h %{buildroot}%{_includedir}/
install -m0644 libtiff/tif_dir.h %{buildroot}%{_includedir}/

%files progs
%{_bindir}/*
%doc %{_mandir}/man1/*

%files -n %{libname}
%{_libdir}/libtiff.so.%{major}*

%files -n %{libxx}
%{_libdir}/libtiffxx.so.%{major}*

%files -n %{devname}
%doc %{_docdir}/tiff-%{version}
%{_includedir}/*.h*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
%doc %{_mandir}/man3/*

%if %{with compat32}
%files -n %{lib32name}
%{_prefix}/lib/libtiff.so.%{major}*

%files -n %{lib32xx}
%{_prefix}/lib/libtiffxx.so.%{major}*

%files -n %{dev32name}
%{_prefix}/lib/*.so
%{_prefix}/lib/pkgconfig/*.pc
%endif
